"""
ESG components seeder — telemetry-driven, per-vehicle, 8 categories.

For each of the 10 surviving fleet vehicles we compute a realistic wear% per
applicable category from the live `vehicle_telemetry` row (mileage, behaviour
counters, ABS/ESC interventions, battery SOH, engine runtime, etc.) and
insert one `components` row per (vehicle, category, position) pair.

Categories — picked because they map cleanly onto signals our OBD-II + UNIPOL
blackbox actually carries:

    universal        : tire (FL/FR/RL/RR), brake_pad (front/rear),
                       brake_disc (front/rear), suspension_damper (FL/FR/RL/RR),
                       aux_12v_battery
    ICE / hybrid     : engine_oil
    diesel only      : dpf  (particulate filter)
    BEV / hybrid     : ev_battery

For high-mileage vehicles we also insert HISTORICAL `stocked` rows that
represent components previously swapped out and now feeding the second-life
ledger. Target: ~50 stocked rows across the fleet, hand-tuned per vehicle.

Idempotent: gated by the `esg_components_v2` marker in `_seeder_state`.
Drop that row to force a clean re-seed (the seeder wipes + re-inserts all
component rows for the 10 surviving VINs).
"""
import json
import math
import random
import sqlite3
from datetime import date, timedelta

from .database_manager import DatabaseManager


# ──────────────────────────────────────────────────────────────────────────
# 1. Schema migrations (idempotent ALTER TABLE).
# ──────────────────────────────────────────────────────────────────────────
_COMPONENT_MIGRATIONS = [
    "ALTER TABLE components ADD COLUMN serial_number TEXT",
    "ALTER TABLE components ADD COLUMN brand TEXT",
    "ALTER TABLE components ADD COLUMN model_name TEXT",
    "ALTER TABLE components ADD COLUMN specs_json TEXT",
    "ALTER TABLE components ADD COLUMN health_status TEXT",
    "ALTER TABLE components ADD COLUMN installed_date DATE",
    "ALTER TABLE components ADD COLUMN installed_km REAL",
    "ALTER TABLE components ADD COLUMN removed_date DATE",
    "ALTER TABLE components ADD COLUMN removed_km REAL",
    "ALTER TABLE components ADD COLUMN removal_reason TEXT",
    "ALTER TABLE components ADD COLUMN ai_recommendation TEXT",
    "ALTER TABLE components ADD COLUMN ai_reasoning TEXT",
    "ALTER TABLE components ADD COLUMN recovery_value_eur REAL",
    "ALTER TABLE components ADD COLUMN co2_saved_kg REAL",
    "ALTER TABLE components ADD COLUMN destination_facility TEXT",
    "ALTER TABLE components ADD COLUMN created_at DATETIME",
    "ALTER TABLE components ADD COLUMN updated_at DATETIME",
]

_MARKER = "esg_components_v2"


# ──────────────────────────────────────────────────────────────────────────
# 2. Catalogue — blueprints per category.
#    (brand, model_name, base_value_eur, base_co2_kg, destination_facility,
#     ai_recommendation)
# ──────────────────────────────────────────────────────────────────────────
_BLUEPRINTS = {
    "tire": [
        ("Pirelli",     "P Zero PZ4",          85.0, 22.0, "Asphalt Recycling",
         "Asphalt Recycling — devulcanised crumb for road paving"),
        ("Michelin",    "Pilot Sport 4 S",     78.0, 19.0, "Asphalt Recycling",
         "Asphalt Recycling — devulcanised crumb for road paving"),
        ("Bridgestone", "Potenza Sport",       72.0, 20.0, "Energy Recovery",
         "Energy Recovery — cement-kiln co-incineration"),
        ("Continental", "PremiumContact 7",    65.0, 18.0, "Asphalt Recycling",
         "Asphalt Recycling — devulcanised crumb for road paving"),
        ("Goodyear",    "EfficientGrip 2",     58.0, 17.0, "Energy Recovery",
         "Energy Recovery — cement-kiln co-incineration"),
    ],
    "brake_pad": [
        ("Brembo",  "OEM Replacement Pads", 38.0, 11.5, "Scrap Metal Smelting",
         "Scrap Metal Smelting — backing-plate recovery"),
        ("Bosch",   "Blue Stamped Pads",    32.0, 10.2, "Scrap Metal Smelting",
         "Scrap Metal Smelting — backing-plate recovery"),
        ("Ferodo",  "Premier Eco",          29.0,  9.6, "Friction Material",
         "Friction Material — re-bonded compound for industrial brakes"),
        ("Textar",  "Epad Performance",     35.0, 10.8, "Scrap Metal Smelting",
         "Scrap Metal Smelting — backing-plate recovery"),
    ],
    "brake_disc": [
        ("Brembo",   "Coated Disc",       68.0,  24.0, "Steel Foundry Reuse",
         "Steel Foundry Reuse — direct re-melt to GGG-150 castings"),
        ("ATE",      "PowerDisc",         62.0,  22.5, "Steel Foundry Reuse",
         "Steel Foundry Reuse — direct re-melt to GGG-150 castings"),
        ("Zimmermann","Sport Coat Z",     72.0,  26.0, "Steel Foundry Reuse",
         "Steel Foundry Reuse — direct re-melt to GGG-150 castings"),
    ],
    "suspension_damper": [
        ("Bilstein",  "B4 OE Replacement", 95.0, 18.5, "Steel & Oil Separation",
         "Steel & Oil Separation — body recycled, hydraulic oil reclaimed"),
        ("Sachs",     "Twin-Tube Standard", 78.0, 16.0, "Steel & Oil Separation",
         "Steel & Oil Separation — body recycled, hydraulic oil reclaimed"),
        ("KYB",       "Excel-G",           72.0, 15.5, "Steel & Oil Separation",
         "Steel & Oil Separation — body recycled, hydraulic oil reclaimed"),
        ("Monroe",    "Original",          68.0, 14.8, "Steel & Oil Separation",
         "Steel & Oil Separation — body recycled, hydraulic oil reclaimed"),
    ],
    "aux_12v_battery": [
        ("Varta",  "Blue Dynamic E11",  42.0, 28.0, "Lead-Acid Recycling",
         "Lead-Acid Recycling — sealed loop (98% closed-loop recovery)"),
        ("Bosch",  "S4 Silver",         38.0, 26.0, "Lead-Acid Recycling",
         "Lead-Acid Recycling — sealed loop (98% closed-loop recovery)"),
        ("Exide",  "Premium Carbon Boost", 45.0, 30.0, "Lead-Acid Recycling",
         "Lead-Acid Recycling — sealed loop (98% closed-loop recovery)"),
    ],
    "engine_oil": [
        ("Castrol", "EDGE 5W-30",  18.0, 8.5, "Used-Oil Refining",
         "Used-Oil Refining — base-stock re-distillation to lubricant grade"),
        ("Mobil",   "1 ESP 5W-30", 19.0, 8.8, "Used-Oil Refining",
         "Used-Oil Refining — base-stock re-distillation to lubricant grade"),
        ("Eni",     "i-Sint Tech P 5W-30", 17.0, 8.2, "Used-Oil Refining",
         "Used-Oil Refining — base-stock re-distillation to lubricant grade"),
    ],
    "dpf": [
        ("Bosal",  "DPF Replacement", 320.0, 95.0, "Precious Metal Recovery",
         "Precious Metal Recovery — Pt/Pd/Rh extraction from washcoat"),
        ("Walker", "Diesel Particulate Filter", 295.0, 88.0, "Precious Metal Recovery",
         "Precious Metal Recovery — Pt/Pd/Rh extraction from washcoat"),
    ],
    "ev_battery": [
        ("LG Chem",      "RESU16H Module",  4200.0, 1180.0, "Grid Storage",
         "Grid Storage — second-life stationary buffer at solar farm"),
        ("CATL",         "Qilin Pack v2",   3850.0, 1090.0, "Grid Storage",
         "Grid Storage — second-life stationary buffer at solar farm"),
        ("Panasonic",    "NCA 4680 Cell",   3950.0, 1150.0, "Black Mass Recycling",
         "Black Mass Recycling — Li/Co/Ni hydrometallurgy"),
        ("Samsung SDI",  "P5 Module",       3400.0,  980.0, "Black Mass Recycling",
         "Black Mass Recycling — Li/Co/Ni hydrometallurgy"),
    ],
}


# ──────────────────────────────────────────────────────────────────────────
# 3. Wear-formulas. Each takes (telemetry-row, vehicle-info, position)
#    and returns wear_pct ∈ [0, 100]. Higher = closer to EOL.
#
#    These are deliberately telemetry-grounded so the seeded value matches
#    what the driver's behaviour + the live counters would predict on a
#    real OBD-II + UNIPOL blackbox stream.
# ──────────────────────────────────────────────────────────────────────────
def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def _years_since(date_str: str) -> float:
    if not date_str:
        return 0.0
    try:
        y, m, d = (int(p) for p in date_str[:10].split("-"))
        return max(0.0, (date.today() - date(y, m, d)).days / 365.25)
    except (ValueError, TypeError):
        return 0.0


# How much of the vehicle's current odometer this category has actually
# accumulated (the rest belongs to a previous component that's already in the
# stocked / EOL pool). These are CONSUMABLES → "km since last replacement".
# For lifetime components (suspension, ev_battery) we use the full odometer.
_TYPICAL_KM_SINCE_INSTALL = {
    "tire":              25_000,
    "brake_pad":         35_000,
    "brake_disc":        70_000,
    "aux_12v_battery":   60_000,
    "engine_oil":        12_000,
    "dpf":               130_000,
}
# Expected service life of a fresh part — used as the denominator of the
# base wear ratio (wear = km_since_install / lifetime × 100).
_TYPICAL_LIFETIME_KM = {
    "tire":              60_000,
    "brake_pad":         55_000,
    "brake_disc":        180_000,
    "suspension_damper": 160_000,
    "aux_12v_battery":   90_000,
    "engine_oil":        15_000,
    "dpf":               200_000,
}


def _km_on_part(total_km: float, category: str) -> float:
    """Effective km accumulated on the currently-installed component."""
    if category in ("suspension_damper", "ev_battery"):
        return total_km  # lifetime parts — never replaced
    typical = _TYPICAL_KM_SINCE_INSTALL.get(category, 25_000)
    return min(total_km, typical)


def wear_tire(tel, info, position):
    """Tread wear: km on current set + cornering + braking aggression."""
    km   = _km_on_part(tel.get("current_odometer_km") or 0, "tire")
    hb   = tel.get("hard_brake_count") or 0
    ha   = tel.get("hard_accel_count") or 0
    hc   = tel.get("hard_cornering_count") or 0
    abs_n= tel.get("abs_activations_count") or 0
    hwy  = (tel.get("highway_driving_pct") or 50) / 100.0

    base = (km / _TYPICAL_LIFETIME_KM["tire"]) * 100   # 100% at 60 000 km

    behaviour_bonus = (hb * 0.020 + ha * 0.015 + hc * 0.025 + abs_n * 0.08)
    # Urban driving wears tires faster than highway (more cornering + braking).
    behaviour_bonus *= (1.4 - 0.6 * hwy)

    # Per-corner skew: front=1.10, rear=0.90; outer corners on a left-hand-drive
    # market wear slightly more on the right.
    corner_skew = {
        "FL": 1.10, "FR": 1.06,
        "RL": 0.92, "RR": 0.94,
    }.get(position, 1.0)

    return _clamp(base * corner_skew + behaviour_bonus * corner_skew)


def wear_brake_pad(tel, info, position):
    """Pad wear from hard-brake + ABS events. BEVs offset by regen %."""
    km    = _km_on_part(tel.get("current_odometer_km") or 0, "brake_pad")
    hb    = tel.get("hard_brake_count") or 0
    abs_n = tel.get("abs_activations_count") or 0
    urb   = (tel.get("urban_driving_pct") or 30) / 100.0
    regen = (tel.get("regen_braking_pct") or 0) / 100.0
    powertrain = (info.get("powertrain") or "").upper()

    base = (km / _TYPICAL_LIFETIME_KM["brake_pad"]) * 100   # 100% at 55 000 km on this set

    behaviour = hb * 0.10 + abs_n * 0.25
    behaviour *= (0.7 + 0.9 * urb)  # urban 100% → 1.6×; urban 10% → 0.79×

    # Regen credit on EV/Hybrid — BEVs use mechanical brake ~55% less.
    if "BEV" in powertrain or "HYB" in powertrain:
        behaviour *= (1.0 - 0.55 * (regen if regen else 0.6))

    # Front pads take ~1.3× the load of rear pads.
    front_skew = 1.25 if position == "front" else 0.85
    return _clamp(base * front_skew + behaviour * front_skew * 0.4)


def wear_brake_disc(tel, info, position):
    """Discs outlive pads ~3×. Same drivers, scaled."""
    pad_w = wear_brake_pad(tel, info, position)
    return _clamp(pad_w * 0.42)


def wear_suspension_damper(tel, info, position):
    """Damper fatigue from km + accel_z spikes (proxied by hard_brake +
    hard_cornering). Expected life ~160 000 km."""
    km   = _km_on_part(tel.get("current_odometer_km") or 0, "suspension_damper")
    hb   = tel.get("hard_brake_count") or 0
    hc   = tel.get("hard_cornering_count") or 0
    urb  = (tel.get("urban_driving_pct") or 30) / 100.0

    base = (km / _TYPICAL_LIFETIME_KM["suspension_damper"]) * 100
    behaviour = (hb + hc) * 0.018
    behaviour *= (1.0 + 0.8 * urb)   # urban = more potholes / speed bumps

    corner_skew = {"FL": 1.08, "FR": 1.05, "RL": 0.96, "RR": 0.94}.get(position, 1.0)
    return _clamp(base * corner_skew + behaviour * corner_skew)


def wear_aux_12v_battery(tel, info, position):
    """12 V battery: age + idle (sulfation) + voltage health.

    A flooded lead-acid lasts ~6 years. Idle minutes hammer it (engine off
    + lights/HVAC on). Cold-cranking voltage <12.4 V is a red flag.
    """
    # Effective service time of this battery (last replacement) — for old cars
    # the battery has already been swapped at least once.
    age_yr = _years_since(info.get("production_date"))
    service_yr = min(age_yr, 4.5)   # current battery is at most 4.5 yr old
    idle  = (tel.get("idle_time_s") or 0) / 60.0  # minutes
    volt  = tel.get("battery_voltage_v") or tel.get("control_module_voltage_v") or 12.6

    base = (service_yr / 6.0) * 100  # 100% at 6 years on this battery
    sulfation = (idle / 240.0) * 12  # +12% per 4 hours of cumulative idle
    voltage_penalty = max(0, (12.6 - volt) * 18)
    return _clamp(base + sulfation + voltage_penalty)


def wear_engine_oil(tel, info, position):
    """Oil degrades with km since last service + hard accel + thermal stress.

    OEMs spec ~15 000 km / 12 months. Hard accel events shear polymer
    modifiers; sustained high coolant temps oxidise the base stock.
    """
    km = _km_on_part(tel.get("current_odometer_km") or 0, "engine_oil")
    ha = tel.get("hard_accel_count") or 0
    coolant = tel.get("coolant_temp_c") or 90

    base = (km / _TYPICAL_LIFETIME_KM["engine_oil"]) * 100   # 100% at 15k km
    shear = ha * 0.03
    thermal = max(0, (coolant - 92) * 1.0)
    return _clamp(base + shear + thermal)


def wear_dpf(tel, info, position):
    """Diesel particulate filter: soot + ash from low-temp urban cycles."""
    km     = _km_on_part(tel.get("current_odometer_km") or 0, "dpf")
    urb    = (tel.get("urban_driving_pct") or 30) / 100.0
    nox    = tel.get("nox_ppm") or 0
    dtcs   = tel.get("dtc_count") or 0
    load   = tel.get("engine_load_pct") or 40

    base = (km / _TYPICAL_LIFETIME_KM["dpf"]) * 100   # 100% at 200k km

    urban_pen = urb * 25     # urban cold cycles can't burn off soot
    nox_pen   = (nox / 100.0) * 8
    dtc_pen   = dtcs * 4
    load_credit = max(0, (load - 35) * -0.04)
    return _clamp(base + urban_pen + nox_pen + dtc_pen + load_credit)


def wear_ev_battery(tel, info, position):
    """EV traction battery: read directly from SOH, with km/SOC-cycle adjust."""
    soh = tel.get("battery_soh_pct")
    if soh is not None:
        base = 100 - soh
    else:
        base = 5.0
    km = tel.get("current_odometer_km") or 0
    # Light km-based aging (fast charging at high SOC accelerates wear).
    cycle_aging = km / 4500.0  # +22% per 100 000 km on top of SOH
    return _clamp(base + cycle_aging)


_WEAR_FN = {
    "tire":               wear_tire,
    "brake_pad":          wear_brake_pad,
    "brake_disc":         wear_brake_disc,
    "suspension_damper":  wear_suspension_damper,
    "aux_12v_battery":    wear_aux_12v_battery,
    "engine_oil":         wear_engine_oil,
    "dpf":                wear_dpf,
    "ev_battery":         wear_ev_battery,
}


# Which categories + positions apply to a given powertrain.
def _categories_for(powertrain: str, fuel_type: str) -> list[tuple[str, str | None]]:
    p = (powertrain or "").upper()
    f = (fuel_type or "").lower()

    # Universal: all four corners of tires + dampers, front/rear pads + discs,
    # plus a single 12V battery.
    items = [
        ("tire", "FL"), ("tire", "FR"), ("tire", "RL"), ("tire", "RR"),
        ("brake_pad", "front"), ("brake_pad", "rear"),
        ("brake_disc", "front"), ("brake_disc", "rear"),
        ("suspension_damper", "FL"), ("suspension_damper", "FR"),
        ("suspension_damper", "RL"), ("suspension_damper", "RR"),
        ("aux_12v_battery", "main"),
    ]
    if "BEV" in p or "HYB" in p:
        items.append(("ev_battery", "main"))
    if p in ("ICE", "HYBRID") or "HYB" in p:
        items.append(("engine_oil", "main"))
    if "diesel" in f:
        items.append(("dpf", "main"))
    return items


# How many historical (stocked) rows to seed for a given vehicle. Aim for
# realistic component-rotation history on high-km / older cars.
def _historical_for(km: float, age_years: float, powertrain: str, fuel: str) -> list[tuple[str, str, str]]:
    """Return [(category, position, removal_reason), …] for prior items."""
    p = (powertrain or "").upper()
    f = (fuel or "").lower()
    out = []

    # Mid-life consumables: one prior brake-pad rotation on anything >35k km
    # (BEVs included — they DO wear pads, just slower).
    if km >= 35_000:
        out += [("brake_pad", "front", "Replaced at scheduled service"),
                ("brake_pad", "rear",  "Replaced at scheduled service")]

    # Tires: one prior set on any car >55k km (typical first replacement window).
    if km >= 55_000:
        out += [("tire", "FL", "Tread below legal minimum"),
                ("tire", "FR", "Tread below legal minimum"),
                ("tire", "RL", "Tread below legal minimum"),
                ("tire", "RR", "Tread below legal minimum")]

    # Heavy-mileage cars get a second pad rotation + first disc set + cabin
    # battery replacement.
    if km >= 90_000:
        out += [("brake_pad", "front", "Second rotation — pads spent"),
                ("brake_pad", "rear",  "Second rotation — pads spent")]
        out += [("brake_disc", "front", "Below minimum thickness"),
                ("brake_disc", "rear",  "Below minimum thickness")]
        out += [("suspension_damper", "FL", "Oil leak / dampening collapsed"),
                ("suspension_damper", "FR", "Oil leak / dampening collapsed")]

    # Diesel specifics: prior DPF on >70k km, prior turbo if >100k km.
    if "diesel" in f and km >= 70_000:
        out += [("dpf", "main", "Filter saturation — non-regenerable")]

    # 12V batteries die every ~5 years — anything >3 yr old has been swapped.
    if age_years >= 3.0:
        out += [("aux_12v_battery", "main", "Failed cranking-voltage test")]

    # Oil: every ICE / Hybrid has multiple prior changes (record the most
    # recent one as the "stocked" sample for the recycling ledger).
    if "BEV" not in p:
        out += [("engine_oil", "main", "Drain at scheduled service")]

    return out


# ──────────────────────────────────────────────────────────────────────────
# 4. Seeder implementation.
# ──────────────────────────────────────────────────────────────────────────
def _ensure_marker_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _seeder_state (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)


def _marker_set(cursor) -> bool:
    row = cursor.execute(
        "SELECT 1 FROM _seeder_state WHERE key=?", (_MARKER,)
    ).fetchone()
    return row is not None


def _set_marker(cursor):
    cursor.execute(
        "INSERT OR REPLACE INTO _seeder_state (key, value) VALUES (?, ?)",
        (_MARKER, "done"),
    )


def _wear_to_status(wear_pct: float) -> str:
    if wear_pct >= 75:   return "critical"
    if wear_pct >= 55:   return "warning"
    return "healthy"


def _specs_for(category: str, vehicle_info: dict, wear_pct: float) -> dict:
    """Realistic per-category spec blob (rendered in the table's expand row)."""
    pt = (vehicle_info.get("powertrain") or "").upper()
    if category == "tire":
        return {"size": "245/40 R19", "tread_depth_mm": round(7.5 * (1 - wear_pct/110) + 1.6, 2),
                "load_index": "97", "speed_rating": "Y"}
    if category == "brake_pad":
        return {"material": "Semi-metallic", "thickness_mm": round(12 * (1 - wear_pct/100), 1)}
    if category == "brake_disc":
        return {"diameter_mm": 345, "thickness_mm": round(28 - wear_pct * 0.04, 2),
                "min_thickness_mm": 25.0}
    if category == "suspension_damper":
        return {"travel_mm": 220, "oil_grade": "ISO 32",
                "type": "Twin-tube hydraulic"}
    if category == "aux_12v_battery":
        return {"capacity_ah": 80, "cca": 800, "chemistry": "AGM"}
    if category == "engine_oil":
        return {"viscosity": "5W-30", "volume_l": 4.5, "acea_class": "C3"}
    if category == "dpf":
        return {"substrate": "Cordierite", "soot_loaded_g": round(wear_pct * 0.7, 1),
                "ash_loaded_g": round(wear_pct * 0.25, 1)}
    if category == "ev_battery":
        # Pull realistic kWh per model
        model = (vehicle_info.get("model_name") or "").lower()
        if "grecale" in model:    kwh = 105.0
        elif "model 3" in model:  kwh = 75.0
        elif "500e" in model:     kwh = 42.0
        elif "yaris" in model:    kwh = 1.3   # hybrid traction pack
        else:                     kwh = 60.0
        soh = max(60.0, 100 - wear_pct)
        return {"capacity_kwh": kwh, "soh_percent": round(soh, 1),
                "chemistry": "Li-NMC" if pt == "BEV" else "Ni-MH"}
    return {}


def _installed_date(info: dict, km: float, age_years: float, category: str) -> tuple[str, float]:
    """Sensible install-date + install-km for a current 'installed' row.

    Uses the same `_TYPICAL_KM_SINCE_INSTALL` table that `_km_on_part` reads
    so the wear% and install-km tell a self-consistent story.
    """
    today = date.today()
    offset_km = min(km, _TYPICAL_KM_SINCE_INSTALL.get(category, 0))
    installed_km = max(0, km - offset_km)
    # Translate the km-offset into elapsed time (assume avg 33 km/day → 12 000 km/yr).
    days_offset = int(offset_km / 33.0)
    d = today - timedelta(days=days_offset)
    return d.isoformat(), installed_km


def _vehicle_rows(cursor) -> list[dict]:
    """Pull the 10 (or however-many) surviving vehicles + their telemetry."""
    rows = cursor.execute("""
        SELECT v.vin, v.production_date, v.registration_date,
               cm.manufacturer, cm.model_name, cm.powertrain, cm.drivetrain,
               vt.*
        FROM vehicles v
        JOIN car_models cm ON v.model_id = cm.id
        LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
    """).fetchall()
    return [dict(r) for r in rows]


def _wipe_components(cursor, vins: list[str]):
    """Hard-reset the components table for these vehicles (and orphans)."""
    if not vins:
        return
    placeholders = ",".join("?" * len(vins))
    cursor.execute(
        f"DELETE FROM components WHERE vehicle_vin IN ({placeholders}) OR vehicle_vin IS NULL",
        vins,
    )


def _make_serial(vin: str, category: str, position: str | None, suffix: str = "") -> str:
    pos = (position or "X").upper()
    cat_prefix = {
        "tire": "TYR", "brake_pad": "BPD", "brake_disc": "BDC",
        "suspension_damper": "SUS", "aux_12v_battery": "B12",
        "engine_oil": "OIL", "dpf": "DPF", "ev_battery": "EVB",
    }.get(category, category[:3].upper())
    base = f"{cat_prefix}-{vin[-6:]}-{pos[:2]}"
    return f"{base}-{suffix}" if suffix else base


def _ai_reasoning(category: str, wear: float, tel: dict, info: dict) -> str:
    """Short, telemetry-grounded justification for the AI Reasoning panel."""
    km  = tel.get("current_odometer_km") or 0
    hb  = tel.get("hard_brake_count") or 0
    hc  = tel.get("hard_cornering_count") or 0
    urb = tel.get("urban_driving_pct") or 0
    pt  = (info.get("powertrain") or "").upper()
    pieces = []
    if category == "tire":
        pieces.append(f"{km:,.0f} km on tread")
        if hc > 50: pieces.append(f"{hc} harsh-cornering events")
    elif category == "brake_pad":
        if "BEV" in pt:
            pieces.append("regen-braking shoulders 55% of stops")
        pieces.append(f"{hb} hard-brake events")
        if urb > 50: pieces.append(f"{urb:.0f}% urban driving")
    elif category == "brake_disc":
        pieces.append(f"{km:,.0f} km / pads on second rotation typical")
    elif category == "suspension_damper":
        pieces.append(f"{km:,.0f} km / urban {urb:.0f}% (potholes)")
    elif category == "aux_12v_battery":
        idle = (tel.get("idle_time_s") or 0) / 3600.0
        pieces.append(f"age {_years_since(info.get('production_date')):.1f} yr")
        if idle > 0.5: pieces.append(f"{idle:.1f} h cumulative idle (sulfation)")
    elif category == "engine_oil":
        runh = (tel.get("engine_runtime_s") or 0) / 3600.0
        pieces.append(f"{runh:.0f} engine-hours since last change")
    elif category == "dpf":
        nox = tel.get("nox_ppm") or 0
        pieces.append(f"NOx {nox:.0f} ppm, urban {urb:.0f}%")
        if (tel.get("dtc_count") or 0) > 0:
            pieces.append(f"{tel['dtc_count']} active DTC(s)")
    elif category == "ev_battery":
        soh = tel.get("battery_soh_pct") or 100
        pieces.append(f"SOH {soh:.0f}%, {km:,.0f} km cycled")
    return " · ".join(pieces) + f" → {wear:.0f}% wear estimated."


def _seed_vehicle(cursor, v: dict):
    """Insert installed + historical-stocked rows for one vehicle."""
    vin   = v["vin"]
    km    = v.get("current_odometer_km") or 0
    age   = _years_since(v.get("production_date"))
    pt    = v.get("powertrain") or ""
    fuel  = v.get("fuel_type") or ""
    today = date.today()

    seeded = 0
    # ── Installed (current) components ────────────────────────────────────
    for cat, pos in _categories_for(pt, fuel):
        wear = _WEAR_FN[cat](v, v, pos)
        brand, model, base_val, base_co2, dest, recommendation = random.choice(_BLUEPRINTS[cat])
        # No recovery_value/co2 while still on the road → installed.
        installed_date, installed_km = _installed_date(v, km, age, cat)
        cursor.execute("""
            INSERT INTO components (
                vehicle_vin, category, position, wear_percent, status,
                serial_number, brand, model_name, specs_json, health_status,
                installed_date, installed_km,
                ai_reasoning,
                recovery_value_eur, co2_saved_kg,
                created_at, updated_at
            ) VALUES (?,?,?,?,?, ?,?,?,?,?, ?,?, ?, ?,?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            vin, cat, pos, round(wear, 1), "installed",
            _make_serial(vin, cat, pos),
            brand, model, json.dumps(_specs_for(cat, v, wear)),
            _wear_to_status(wear),
            installed_date, installed_km,
            _ai_reasoning(cat, wear, v, v),
            None, None,
        ))
        seeded += 1

    # ── Historical (stocked / EOL) components ─────────────────────────────
    for idx, (cat, pos, reason) in enumerate(_historical_for(km, age, pt, fuel)):
        # Historical rows are end-of-life: wear pegged 85-95%, valued, with
        # the AI recommendation set so the Inventory ledger lights up.
        wear = round(random.uniform(85.0, 96.0), 1)
        brand, model, base_val, base_co2, dest, recommendation = random.choice(_BLUEPRINTS[cat])
        # Synthetic install/remove timeline anchored to the vehicle's odometer.
        removed_km = max(km - 4_000, km * 0.55)
        removed_date = (today - timedelta(days=random.randint(60, 420))).isoformat()
        install_offset = {
            "brake_pad": 35_000, "brake_disc": 90_000, "tire": 50_000,
            "dpf": 120_000, "aux_12v_battery": 60_000,
        }.get(cat, 50_000)
        installed_km = max(0, removed_km - install_offset)
        installed_date = (today - timedelta(days=random.randint(450, 1500))).isoformat()

        # Recovery value scales with wear% inverse (less wear → more value)
        # but historical EOL items still fetch ~60-80% of base.
        value_eur = round(base_val * (0.55 + 0.35 * random.random()), 2)
        co2_kg    = round(base_co2 * (0.85 + 0.30 * random.random()), 1)

        cursor.execute("""
            INSERT INTO components (
                vehicle_vin, category, position, wear_percent, status,
                serial_number, brand, model_name, specs_json, health_status,
                installed_date, installed_km,
                removed_date, removed_km, removal_reason,
                ai_recommendation, ai_reasoning,
                recovery_value_eur, co2_saved_kg, destination_facility,
                created_at, updated_at
            ) VALUES (?,?,?,?,?, ?,?,?,?,?, ?,?, ?,?,?, ?,?, ?,?,?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            vin, cat, pos, wear, "stocked",
            _make_serial(vin, cat, pos, suffix=f"H{idx}"),
            brand, model, json.dumps(_specs_for(cat, v, wear)),
            "end_of_life",
            installed_date, installed_km,
            removed_date, removed_km, reason,
            recommendation,
            f"End-of-life — {reason.lower()}. Routed to {dest} for highest "
            f"recovery yield ({brand} {model} grade).",
            value_eur, co2_kg, dest,
        ))
        seeded += 1

    return seeded


# ──────────────────────────────────────────────────────────────────────────
# 5. Entry point.
# ──────────────────────────────────────────────────────────────────────────
def migrate_and_seed():
    """Migrate schema + populate components from telemetry. Idempotent."""
    conn = DatabaseManager.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Run column ALTERs (safe on duplicate).
    for sql in _COMPONENT_MIGRATIONS:
        try:
            cursor.execute(sql)
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                raise
    conn.commit()

    # 2. Marker check — only re-seed when version bumps.
    _ensure_marker_table(cursor)
    if _marker_set(cursor):
        conn.close()
        return

    random.seed(2026)  # deterministic demo

    # 3. Fetch surviving vehicles and wipe their old component rows.
    vehicles = _vehicle_rows(cursor)
    vins = [v["vin"] for v in vehicles]
    _wipe_components(cursor, vins)

    # 4. Seed everything.
    total = 0
    for v in vehicles:
        if not v.get("vin"):
            continue
        total += _seed_vehicle(cursor, v)

    # 5. Mark done.
    _set_marker(cursor)
    conn.commit()
    conn.close()
    print(f"♻️  esg_seeder: populated {total} component rows across {len(vehicles)} vehicles.")


if __name__ == "__main__":
    migrate_and_seed()
