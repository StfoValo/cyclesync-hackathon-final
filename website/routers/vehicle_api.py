import os
import uuid
import json as _json
from typing import Optional
from fastapi import APIRouter, Body, Request
from models.data_manager.database_manager import DatabaseManager
from models.driver_models.brake_model import BrakeModel
from models.driver_models.tire_model import TireModel

router = APIRouter()

@router.get("/api/driver/{driver_id}")
def get_driver_profile(driver_id: int):
    """
    Get driver profile and their linked garage. 
    Reads LIVE data directly from cyclesync.db.
    """
    print(f"🚦 [API HIT] /api/driver/{driver_id} called.")
    
    try:
        conn = DatabaseManager.get_connection()
        conn.row_factory = __import__('sqlite3').Row 
        cursor = conn.cursor()
        
        # 1. Fetch Driver Profile
        driver = cursor.execute(
            "SELECT * FROM driver_accounts WHERE id=?", (driver_id,)
        ).fetchone()
        
        if not driver:
            conn.close()
            return {"error": "Driver not found"}
            
        # 2. Fetch Linked Vehicles
        vehicles = cursor.execute("""
            SELECT 
                v.vin, v.plate_number, cm.model_name, cm.manufacturer, 
                v.production_date, v.color, cm.powertrain, v.vehicle_category,
                vt.driving_score, vt.current_odometer_km
            FROM driver_vehicles dv
            JOIN vehicles v ON dv.vin = v.vin
            JOIN car_models cm ON v.model_id = cm.id
            LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
            WHERE dv.driver_id = ?
            ORDER BY dv.added_at
        """, (driver_id,)).fetchall()
        
        conn.close()

        # 3. Format the response and dynamically map the images!
        formatted_vehicles = []
        for v in vehicles:
            # Safely format strings: 'Maserati' -> 'maserati', 'Grecale Folgore' -> 'grecale_folgore'
            mfr_clean = (v["manufacturer"] or "unknown").lower().replace(" ", "_")
            mdl_clean = (v["model_name"] or "unknown").lower().replace(" ", "_")
            
            # --- THE FIX: Updated to .webp for the car photo ---
            photo_url = f"/storage/car_photos/{mfr_clean}_{mdl_clean}.webp"
            
            # (If your maserati logo is actually a .png, change this next line to .png)
            logo_url = f"/storage/logos/{mfr_clean}_logo.jpg" 
            
            formatted_vehicles.append({
                "vin": v["vin"],
                "plate": v["plate_number"] or "N/A",
                "model": v["model_name"],
                "manufacturer": v["manufacturer"],
                "year": int(v["production_date"][:4]) if v["production_date"] else None,
                "color": v["color"],
                "powertrain": v["powertrain"],
                "body_type": v["vehicle_category"],
                "vsi_score": v["driving_score"],
                "odometer_km": v["current_odometer_km"],
                "is_pinned": v["vin"] == driver["pinned_vin"],
                "photo_url": photo_url,
                "logo_url": logo_url
            })
        
        print(f"✅ [SUCCESS] Found {len(formatted_vehicles)} linked vehicles.")
        
        return {
            "id": driver["id"],
            "email": driver["email"],
            "display_name": driver["display_name"],
            "phone": driver["phone"],
            "pinned_vin": driver["pinned_vin"],
            "vehicles": formatted_vehicles
        }
        
    except Exception as e:
        print(f"🚨 [CRITICAL DB ERROR]: {str(e)}")
        return {"error": f"Database failure: {str(e)}"}

# ──────────────────────────────────────────────────────────────────────────
# Per-category lifecycle metadata used by /component-life.
#
# Each entry tells the driver UI how long a fresh part of this category lasts
# in km (so we can compute "est_remaining_km" from health%) plus the wear-%
# thresholds that turn the card amber / red, plus the IT/EN consequence
# strings the consumer app shows.
# ──────────────────────────────────────────────────────────────────────────
_COMPONENT_LIFE_META = {
    "tire": {
        "lifetime_km": 60_000, "warn_at": 60, "crit_at": 80,
        "cons_good": "Battistrada in buono stato.",
        "cons_warn": "Battistrada in usura — pianifica la sostituzione.",
        "cons_crit": "Battistrada vicino al limite legale — sostituisci subito.",
    },
    "brake_pad": {
        "lifetime_km": 55_000, "warn_at": 60, "crit_at": 80,
        "cons_good": "Pastiglie in ottime condizioni.",
        "cons_warn": "Pastiglie in fase di usura — programmare il controllo.",
        "cons_crit": "Pastiglie a rischio — sostituzione urgente.",
    },
    "brake_disc": {
        "lifetime_km": 180_000, "warn_at": 70, "crit_at": 88,
        "cons_good": "Dischi in buono stato.",
        "cons_warn": "Dischi prossimi al limite minimo — controllo consigliato.",
        "cons_crit": "Dischi sotto soglia minima — sostituzione obbligatoria.",
    },
    "suspension_damper": {
        "lifetime_km": 160_000, "warn_at": 60, "crit_at": 80,
        "cons_good": "Ammortizzatori reattivi.",
        "cons_warn": "Ammortizzatori in calo di rendimento.",
        "cons_crit": "Ammortizzatori da sostituire — perdita di smorzamento.",
    },
    "aux_12v_battery": {
        "lifetime_km": 90_000, "warn_at": 60, "crit_at": 80,
        "cons_good": "Batteria 12 V sana.",
        "cons_warn": "Batteria 12 V indebolita — controllo a freddo consigliato.",
        "cons_crit": "Batteria 12 V vicina al guasto — sostituzione raccomandata.",
    },
    "engine_oil": {
        "lifetime_km": 15_000, "warn_at": 65, "crit_at": 85,
        "cons_good": "Olio motore in buone condizioni.",
        "cons_warn": "Olio motore in degrado — pianifica il tagliando.",
        "cons_crit": "Olio motore esausto — tagliando urgente.",
    },
    "dpf": {
        "lifetime_km": 200_000, "warn_at": 70, "crit_at": 88,
        "cons_good": "Filtro antiparticolato sano.",
        "cons_warn": "DPF in saturazione — rigenerazione consigliata.",
        "cons_crit": "DPF saturo — sostituzione/lavaggio richiesto.",
    },
    "ev_battery": {
        "lifetime_km": 250_000, "warn_at": 18, "crit_at": 30,
        "cons_good": "Batteria di trazione sana.",
        "cons_warn": "SOH in calo — usa la ricarica veloce con parsimonia.",
        "cons_crit": "SOH ridotto — autonomia compromessa.",
    },
}

_DTC_DESCRIPTIONS = {
    "P0420": "Catalyst System Efficiency Below Threshold (Bank 1)",
    "P0171": "System Too Lean (Bank 1)",
    "P0300": "Random / Multiple Cylinder Misfire Detected",
    "P0301": "Cylinder 1 Misfire Detected",
    "P0302": "Cylinder 2 Misfire Detected",
    "P0303": "Cylinder 3 Misfire Detected",
    "P0304": "Cylinder 4 Misfire Detected",
    "P0401": "EGR Flow Insufficient",
    "P0455": "Evaporative Emission Large Leak Detected",
    "P0606": "PCM Processor Fault",
    "P0700": "Transmission Control System Malfunction",
    "U0100": "Lost Communication with ECM/PCM",
    "P2002": "Diesel Particulate Filter Efficiency Below Threshold",
    "P2463": "Diesel Particulate Filter Restriction — Soot Accumulation",
}


def _wear_to_urgency(wear_pct: float, meta: dict) -> str:
    if wear_pct >= meta["crit_at"]: return "critical"
    if wear_pct >= meta["warn_at"]: return "warning"
    return "good"


def _build_vsi_tips(telemetry, components):
    """Telemetry-driven VSI improvement tips. Returns a list of ≤4 strings."""
    tips = []
    hb  = telemetry["hard_brake_count"] or 0
    ha  = telemetry["hard_accel_count"] or 0
    hc  = telemetry["hard_cornering_count"] or 0
    abs_n = telemetry["abs_activations_count"] or 0
    urb = telemetry["urban_driving_pct"] or 0
    night = telemetry["night_driving_pct"] or 0
    idle = (telemetry["idle_time_s"] or 0) / 60.0
    soh = telemetry["battery_soh_pct"]

    if hb > 50:
        tips.append(f"Riduci le frenate brusche ({hb} eventi): le pastiglie possono durare il 18% in più.")
    if ha > 80:
        tips.append(f"Accelerazioni dolci ({ha} eventi) — meno usura e fino al 7% di consumo in meno.")
    if hc > 60:
        tips.append(f"Curva con meno aggressività ({hc} eventi) — gli pneumatici dureranno più a lungo.")
    if abs_n > 15:
        tips.append(f"Mantieni più distanza di sicurezza: {abs_n} interventi ABS rilevati.")
    if urb > 60:
        tips.append("Inserisci viaggi extra-urbani: aiutano la rigenerazione del DPF / scarica eolian e.")
    if night > 35:
        tips.append("Programma controlli batteria 12 V: la guida notturna sottopone l'impianto a carico extra.")
    if idle > 60:
        tips.append("Limita il minimo prolungato: la batteria 12 V si solfatizza più velocemente.")
    if soh is not None and soh < 90:
        tips.append(f"SOH batteria al {soh:.0f}% — preferisci AC charging quando possibile.")

    if not tips:
        tips = [
            "Eccellente stile di guida — continua così per mantenere il VSI alto.",
            "Tieni la pressione gomme a 2.3 bar per un 5% in meno di CO₂.",
        ]
    return tips[:4]


def _build_dtc_alerts(telemetry):
    """Read dtc_codes_json + pending_dtc_codes_json and decorate with descriptions."""
    out = []
    for col, severity in (("dtc_codes_json", "active"),
                          ("pending_dtc_codes_json", "pending")):
        raw = telemetry[col] if col in telemetry.keys() else None
        if not raw:
            continue
        try:
            codes = _json.loads(raw)
        except Exception:
            continue
        if not isinstance(codes, list):
            continue
        for code in codes:
            out.append({
                "code": code,
                "description": _DTC_DESCRIPTIONS.get(code, "Codice diagnostico generico"),
                "severity": severity,
            })
    return out


@router.get("/api/driver/vehicle/{vin}/component-life")
def get_component_lifecycle(vin: str):
    """Driver-app component-health payload.

    Returns the same shape the consumer app always expected
    (`components[]`, `vsi_tips[]`) plus a new `dtc_alerts[]` array. The
    components list now covers all 8 ESG-seeder categories (tire ×4,
    brake_pad ×2, brake_disc ×2, suspension_damper ×4, aux_12v_battery,
    engine_oil, dpf, ev_battery) — every card gets a localised
    `consequence` string + an `est_remaining_km` derived from
    `_COMPONENT_LIFE_META` so the urgency lights up consistently.
    """
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()

    telemetry = cursor.execute(
        "SELECT * FROM vehicle_telemetry WHERE vin=?", (vin,)
    ).fetchone()
    if not telemetry:
        conn.close()
        return {"error": "Vehicle or telemetry not found"}

    # All currently-installed components for this vehicle (8-cat schema).
    rows = cursor.execute("""
        SELECT category, position, wear_percent, brand, model_name,
               health_status, ai_reasoning, installed_km
        FROM components
        WHERE vehicle_vin = ? AND status = 'installed'
        ORDER BY category, position
    """, (vin,)).fetchall()

    # Also pull mounted-tire tread for the per-corner consequence string
    # (the components.tire rows alone don't carry mm — that's still in
    # `mounted_tires`). Falls back gracefully if the table is empty.
    tread_by_pos = {}
    try:
        for t in cursor.execute("""
            SELECT m.position, m.current_tread_depth_mm
            FROM mounted_tires m WHERE m.vin = ?
        """, (vin,)).fetchall():
            tread_by_pos[t["position"]] = t["current_tread_depth_mm"]
    except Exception:
        pass

    conn.close()

    components_payload = []
    for c in rows:
        cat  = c["category"]
        meta = _COMPONENT_LIFE_META.get(cat)
        if not meta:
            continue
        wear = c["wear_percent"] or 0.0
        health_pct = max(0.0, 100.0 - wear)
        est_km = max(0, int(meta["lifetime_km"] * (health_pct / 100.0)))
        urgency = _wear_to_urgency(wear, meta)

        # Per-category consequence string. Tires get the tread mm if we have it.
        if cat == "tire" and c["position"] in tread_by_pos:
            cons = f"Battistrada residuo: {tread_by_pos[c['position']]} mm"
        else:
            cons = meta[f"cons_{urgency[:4]}"] if urgency in ("good", "warning") \
                   else meta["cons_crit"]

        components_payload.append({
            "category":         cat,
            "position":         c["position"],
            "health_pct":       round(health_pct, 1),
            "wear_percent":     round(wear, 1),
            "est_remaining_km": est_km,
            "urgency":          urgency,
            "consequence":      cons,
            "brand":            c["brand"],
            "model":            c["model_name"],
            "ai_reasoning":     c["ai_reasoning"],
        })

    return {
        "vsi_tips":   _build_vsi_tips(telemetry, components_payload),
        "dtc_alerts": _build_dtc_alerts(telemetry),
        "components": components_payload,
        "vsi_score":  telemetry["driving_score"],
        "odometer_km": telemetry["current_odometer_km"],
    }

@router.put("/api/driver/{driver_id}/pin/{vin}")
def pin_vehicle(driver_id: int, vin: str):
    """Updates the driver's default vehicle."""
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE driver_accounts SET pinned_vin=? WHERE id=?", (vin, driver_id))
    conn.commit()
    conn.close()
    return {"status": "ok", "pinned_vin": vin}

@router.post("/api/driver/{driver_id}/vehicles")
def link_vehicle(driver_id: int, data: dict = Body(...)):
    """Links a new vehicle to the driver's garage via VIN or Plate."""
    search = data.get("search", "").strip().upper().replace(" ", "").replace("-", "")
    if not search:
        return {"error": "Please provide a VIN or Plate number."}
        
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    
    # Check if the car exists in the enterprise database
    row = cursor.execute("""
        SELECT vin FROM vehicles 
        WHERE REPLACE(plate_number, ' ', '') = ? OR vin = ?
    """, (search, search)).fetchone()
    
    if not row:
        conn.close()
        return {"error": "Vehicle not found in the network."}
        
    vin = row["vin"]
    
    # Link it to the driver
    try:
        cursor.execute("INSERT INTO driver_vehicles (driver_id, vin) VALUES (?, ?)", (driver_id, vin))
        conn.commit()
    except Exception:
        conn.close()
        return {"error": "This vehicle is already in your garage."}
        
    conn.close()
    return {"status": "ok", "vin": vin}

@router.delete("/api/driver/{driver_id}/vehicles/{vin}")
def unlink_vehicle(driver_id: int, vin: str):
    """Removes a vehicle from the driver's garage."""
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM driver_vehicles WHERE driver_id=? AND vin=?", (driver_id, vin))
    # If they deleted their pinned car, clear the pin
    cursor.execute("UPDATE driver_accounts SET pinned_vin=NULL WHERE id=? AND pinned_vin=?", (driver_id, vin))

    conn.commit()
    conn.close()
    return {"status": "ok"}


@router.post("/api/driver/{driver_id}/maintenance")
def log_maintenance(driver_id: int, data: dict = Body(...)):
    """Log a maintenance event (oil change, tire change, brake service, etc.)."""
    print(f"🚦 [API HIT] /api/driver/{driver_id}/maintenance — {data.get('type', '?')}")
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()

    # The cyclesync.db schema may not yet have maintenance_events; create it on demand.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS maintenance_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_vin TEXT,
            event_date TEXT,
            event_type TEXT,
            description TEXT,
            mileage_km REAL,
            cost_eur REAL,
            facility TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO maintenance_events
            (vehicle_vin, event_date, event_type, description, mileage_km, cost_eur, facility)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("vin", ""),
            data.get("date", ""),
            data.get("type", "scheduled"),
            data.get("description", ""),
            data.get("mileage_km", 0),
            data.get("cost_eur", 0),
            data.get("facility", ""),
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}


# ══════════════════════════════════════════════════════════════════════════
# FLEET REGISTRY API — Insurer-facing vehicle table, filters, passport
# ══════════════════════════════════════════════════════════════════════════

from typing import Optional
import json as _json

@router.get("/api/db/vehicles")
def list_vehicles(
    q: Optional[str] = "",
    region: Optional[str] = None,
    powertrain: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    body_type: Optional[str] = None,
    policy_status: Optional[str] = None,
    has_blackbox: Optional[int] = None,
    sort: Optional[str] = "plate_number",
    order: Optional[str] = "asc",
    page: int = 1,
    per_page: int = 15,
):
    """Paginated vehicle list with full filtering."""
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()

    where = ["1=1"]
    params = []

    if q and len(q) >= 2:
        where.append("(v.plate_number LIKE ? OR v.vin LIKE ? OR v.driver_name LIKE ? OR cm.model_name LIKE ? OR cm.manufacturer LIKE ?)")
        qp = f"%{q}%"
        params.extend([qp, qp, qp, qp, qp])
    if region:
        where.append("v.region_name = ?"); params.append(region)
    if powertrain:
        where.append("cm.powertrain = ?"); params.append(powertrain)
    if manufacturer:
        where.append("cm.manufacturer = ?"); params.append(manufacturer)
    if model:
        where.append("cm.model_name LIKE ?"); params.append(f"%{model}%")
    if body_type:
        where.append("v.vehicle_category = ?"); params.append(body_type)
    if policy_status:
        where.append("v.policy_status = ?"); params.append(policy_status)
    if has_blackbox is not None:
        where.append("v.has_blackbox = ?"); params.append(has_blackbox)

    where_sql = " AND ".join(where)

    sort_map = {
        "plate_number": "v.plate_number", "model": "cm.model_name",
        "vsi_score": "vt.driving_score", "region": "v.region_name",
        "odometer": "vt.current_odometer_km", "driver": "v.driver_name",
        "premium": "v.premium_eur",
    }
    sort_col = sort_map.get(sort, "v.plate_number")
    order_sql = "DESC" if order == "desc" else "ASC"

    count_sql = f"""SELECT COUNT(*) FROM vehicles v
        JOIN car_models cm ON v.model_id = cm.id
        LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
        WHERE {where_sql}"""
    total = cursor.execute(count_sql, params).fetchone()[0]

    offset = (page - 1) * per_page
    sql = f"""SELECT v.vin, v.plate_number, cm.model_name, cm.manufacturer, cm.powertrain,
        v.production_date, v.color, v.vehicle_category, v.region_name, v.driver_name,
        v.policy_status, v.has_blackbox,
        vt.driving_score, vt.current_odometer_km
        FROM vehicles v
        JOIN car_models cm ON v.model_id = cm.id
        LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
        WHERE {where_sql}
        ORDER BY {sort_col} {order_sql}
        LIMIT ? OFFSET ?"""
    params.extend([per_page, offset])
    rows = cursor.execute(sql, params).fetchall()
    conn.close()

    vehicles = []
    for r in rows:
        year = r["production_date"][:4] if r["production_date"] else None
        vehicles.append({
            "vin": r["vin"], "plate": r["plate_number"],
            "model": r["model_name"], "manufacturer": r["manufacturer"],
            "year": int(year) if year else None,
            "powertrain": r["powertrain"],
            "body_type": r["vehicle_category"],
            "region": r["region_name"],
            "driver": r["driver_name"],
            "vsi_score": r["driving_score"],
            "odometer_km": r["current_odometer_km"],
            "has_blackbox": bool(r["has_blackbox"]) if r["has_blackbox"] is not None else False,
            "policy_status": r["policy_status"] or "active",
        })

    return {"vehicles": vehicles, "total": total, "page": page, "per_page": per_page,
            "pages": max(1, (total + per_page - 1) // per_page)}


@router.get("/api/db/vehicles/filters")
def get_filter_values():
    """Return available filter options for the UI dropdowns."""
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    regions = [r[0] for r in cursor.execute("SELECT DISTINCT region_name FROM vehicles WHERE region_name IS NOT NULL ORDER BY region_name").fetchall()]
    manufacturers = [r[0] for r in cursor.execute("SELECT DISTINCT manufacturer FROM car_models WHERE manufacturer IS NOT NULL ORDER BY manufacturer").fetchall()]
    powertrains = [r[0] for r in cursor.execute("SELECT DISTINCT powertrain FROM car_models WHERE powertrain IS NOT NULL ORDER BY powertrain").fetchall()]
    body_types = [r[0] for r in cursor.execute("SELECT DISTINCT vehicle_category FROM vehicles WHERE vehicle_category IS NOT NULL ORDER BY vehicle_category").fetchall()]
    insurers = [r[0] for r in cursor.execute("SELECT DISTINCT insurer FROM vehicles WHERE insurer IS NOT NULL ORDER BY insurer").fetchall()]
    conn.close()
    return {"regions": regions, "manufacturers": manufacturers, "powertrains": powertrains,
            "body_types": body_types, "insurers": insurers}


@router.get("/api/db/vehicles/models/{manufacturer}")
def get_models_by_manufacturer(manufacturer: str):
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    models = [r[0] for r in cursor.execute("SELECT DISTINCT model_name FROM car_models WHERE manufacturer = ? ORDER BY model_name", (manufacturer,)).fetchall()]
    conn.close()
    return {"models": models}


@router.get("/api/db/vehicles/{vin}")
def get_vehicle_passport(vin: str):
    """Full Digital Passport — vehicle identity + insurance + telemetry + components + maintenance."""
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()

    v = cursor.execute("""SELECT v.*, cm.model_name, cm.manufacturer, cm.powertrain, cm.drivetrain,
        cm.power_hp AS cm_hp, cm.displacement_cc AS cm_disp, cm.weight_kg AS cm_wt
        FROM vehicles v JOIN car_models cm ON v.model_id = cm.id WHERE v.vin = ?""", (vin,)).fetchone()
    if not v:
        conn.close()
        return {"error": f"Vehicle '{vin}' not found"}

    telem = cursor.execute("SELECT * FROM vehicle_telemetry WHERE vin = ?", (vin,)).fetchone()
    components = cursor.execute("SELECT * FROM components WHERE vehicle_vin = ? AND status = 'installed' ORDER BY category, position", (vin,)).fetchall()

    # Fetch mounted tires for tread data
    tires = cursor.execute("""
        SELECT m.position, m.current_tread_depth_mm, b.starting_tread_depth_mm, b.expected_lifespan_km
        FROM mounted_tires m
        JOIN tire_blueprints b ON m.blueprint_id = b.id
        WHERE m.vin = ?
    """, (vin,)).fetchall()

    # Maintenance events
    maintenance = cursor.execute(
        "SELECT * FROM maintenance_events WHERE vehicle_vin = ? ORDER BY event_date DESC LIMIT 20", (vin,)
    ).fetchall()

    conn.close()

    year = v["production_date"][:4] if v["production_date"] else None

    # Build component list
    comp_list = []
    for c in components:
        comp_list.append({
            "category": c["category"], "position": c["position"],
            "wear_percent": c["wear_percent"], "status": c["status"],
        })
    for t in tires:
        start = t["starting_tread_depth_mm"]
        curr = t["current_tread_depth_mm"]
        wear = max(0, min(100, ((start - curr) / (start - 1.6)) * 100)) if start > 1.6 else 0
        comp_list.append({
            "category": "tire", "position": t["position"],
            "wear_percent": round(wear, 1), "status": "installed",
        })

    # Build telemetry dict — add has_blackbox flag
    tel_dict = dict(telem) if telem else {}
    tel_dict["has_blackbox"] = bool(v["has_blackbox"]) if v["has_blackbox"] is not None else False

    return {
        "vin": v["vin"], "plate": v["plate_number"],
        "identity": {
            "model": v["model_name"], "manufacturer": v["manufacturer"],
            "year": int(year) if year else None,
            "color": v["color"], "drivetrain": v["drivetrain"],
            "powertrain": v["powertrain"], "body_type": v["vehicle_category"],
            "power_hp": v["power_hp"] or v["cm_hp"],
            "displacement_cc": v["displacement_cc"] or v["cm_disp"],
            "weight_kg": v["weight_kg"] or v["cm_wt"],
            "driver": v["driver_name"],
            "registration_date": v["registration_date"],
            "region": v["region_name"], "city": v["city"], "country": v["country"],
        },
        "insurance": {
            "policy_number": v["policy_number"],
            "policy_type": v["policy_type"],
            "insurer": v["insurer"],
            "premium_eur": v["premium_eur"],
            "policy_start": v["policy_start"],
            "policy_expiry": v["policy_expiry"],
            "policy_status": v["policy_status"] or "active",
            "telematics_discount": v["telematics_discount"],
            "claims_count": v["claims_count"],
        },
        "telemetry": tel_dict,
        "components": comp_list,
        "vsi_score": telem["driving_score"] if telem else None,
        "maintenance": [dict(m) for m in maintenance],
    }


@router.get("/api/vehicles/search")
def search_vehicles_legacy(q: Optional[str] = ""):
    """Quick search for autocomplete — returns compact results."""
    result = list_vehicles(q=q, per_page=50)
    return [{"plate": v["plate"], "model": v["model"], "manufacturer": v["manufacturer"],
             "vsi": v["vsi_score"], "driver": v.get("driver", "")} for v in result["vehicles"]]


@router.get("/api/vehicles/{plate}/passport")
def get_passport_by_plate(plate: str):
    """Find vehicle by plate and return passport."""
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    plate_clean = plate.upper().replace("-", " ").strip().replace(" ", "")
    row = cursor.execute("SELECT vin FROM vehicles WHERE REPLACE(plate_number,' ','') = ?", (plate_clean,)).fetchone()
    conn.close()
    if row:
        return get_vehicle_passport(row["vin"])
    return {"error": f"Vehicle '{plate}' not found"}


# ══════════════════════════════════════════════════════════════════════════
# ADJUSTER PORTAL — Investigation endpoints
# Drives static/partials/adjuster_tab.html + static/js/views/adjuster.js
# ══════════════════════════════════════════════════════════════════════════

@router.get("/api/db/investigations")
def list_investigations(status: Optional[str] = None, priority: Optional[str] = None):
    """List all investigations with optional status/priority filters."""
    print(f"🚦 [API HIT] /api/db/investigations (status={status}, priority={priority})")
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()

    where = ["1=1"]
    params: list = []
    if status:
        where.append("i.status = ?"); params.append(status)
    if priority:
        where.append("i.priority = ?"); params.append(priority)

    rows = cursor.execute(
        f"""
        SELECT i.*, v.plate_number, cm.model_name, cm.manufacturer
        FROM investigations i
        JOIN vehicles v ON i.vehicle_vin = v.vin
        JOIN car_models cm ON v.model_id = cm.id
        WHERE {' AND '.join(where)}
        ORDER BY COALESCE(i.created_at, i.incident_date) DESC
        """,
        params,
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/api/db/investigations/{case_id}")
def get_investigation(case_id: str):
    """Get full investigation detail joined with vehicle, telemetry, components, maintenance."""
    print(f"🚦 [API HIT] /api/db/investigations/{case_id}")
    import json as _json

    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()

    inv = cursor.execute(
        """
        SELECT i.*, v.plate_number, v.driver_name, v.color,
               cm.model_name, cm.manufacturer, cm.powertrain, cm.drivetrain
        FROM investigations i
        JOIN vehicles v ON i.vehicle_vin = v.vin
        JOIN car_models cm ON v.model_id = cm.id
        WHERE i.case_number = ? OR CAST(i.id AS TEXT) = ?
        """,
        (case_id, case_id),
    ).fetchone()

    if not inv:
        conn.close()
        return {"error": f"Investigation '{case_id}' not found"}

    telem = cursor.execute(
        "SELECT * FROM vehicle_telemetry WHERE vin = ?", (inv["vehicle_vin"],)
    ).fetchone()
    components = cursor.execute(
        "SELECT * FROM components WHERE vehicle_vin = ? ORDER BY category, position",
        (inv["vehicle_vin"],),
    ).fetchall()
    maintenance = cursor.execute(
        "SELECT * FROM maintenance_events WHERE vehicle_vin = ? ORDER BY event_date DESC LIMIT 10",
        (inv["vehicle_vin"],),
    ).fetchall()
    conn.close()

    result = dict(inv)
    result["telemetry"] = dict(telem) if telem else None
    result["components"] = [dict(c) for c in components]
    result["maintenance"] = [dict(m) for m in maintenance]
    if result.get("tpms_snapshot_json"):
        try:
            result["tpms_snapshot"] = _json.loads(result["tpms_snapshot_json"])
        except Exception:
            result["tpms_snapshot"] = {}
    return result


@router.get("/api/db/investigations/{case_number}/telemetry-samples")
def get_incident_telemetry_samples(case_number: str):
    """Return the ±5-minute locked telemetry window around the impact.

    Each sample is merged with the vehicle's live `vehicle_telemetry` row so
    every category card has a value at every time index — the time-varying
    columns (speed, accel, brake, GPS, ABS/ESC/airbag, etc.) come from the
    sample, the slow/static ones (TPMS, battery_soh, ambient_temp, driving-
    behaviour counters, ADAS counters, GSM, firmware …) come from the live
    baseline. That way the scrubber never shows "—" on something that the
    blackbox actually emits — only the values that should change actually
    change.
    """
    print(f"🚦 [API HIT] /api/db/investigations/{case_number}/telemetry-samples")
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT * FROM incident_telemetry_samples
        WHERE case_number = ?
        ORDER BY sample_seq
        """,
        (case_number,),
    ).fetchall()

    inv = cursor.execute(
        """
        SELECT i.incident_date, i.incident_type, i.speed_at_impact, i.g_force_max,
               i.g_force_lateral, i.abs_triggered, i.airbag_deployed, i.vehicle_vin
        FROM investigations i WHERE i.case_number = ?
        """,
        (case_number,),
    ).fetchone()

    # Live baseline = the vehicle's current vehicle_telemetry row.
    baseline_dict: dict = {}
    if inv and inv["vehicle_vin"]:
        baseline = cursor.execute(
            "SELECT * FROM vehicle_telemetry WHERE vin = ?",
            (inv["vehicle_vin"],),
        ).fetchone()
        if baseline:
            baseline_dict = dict(baseline)

    conn.close()

    if not rows:
        return {"error": f"No telemetry window stored for {case_number}",
                "samples": []}

    # Sample-only columns that should NEVER fall back to the live baseline
    # (they describe the per-instant state of the incident itself — must
    # update at every tick of the scrubber).
    _DYNAMIC_KEYS = {
        "vehicle_speed_kmh", "throttle_position_pct",
        "brake_pressure_bar", "brake_pedal_pct",
        "steering_angle_deg", "steering_rate_deg_s",
        "accel_x_g", "accel_y_g", "accel_z_g", "accel_total_g",
        "gyro_roll_deg_s", "gyro_pitch_deg_s", "gyro_yaw_deg_s",
        "gps_lat", "gps_lon", "gps_speed_kmh",
        "abs_active", "esc_active", "airbag_deployed",
    }
    # "Powertrain-conditional" keys: a profile MAY emit them (ICE → engine_rpm,
    # coolant_temp_c; BEV → battery_soc_pct), or it may leave them as None
    # because the vehicle has no such sensor. When the sample is None we fall
    # back to the live baseline so the field still renders (e.g. a BEV's
    # baseline reports engine_rpm = 0.0, which is the truthful OBD-II value).
    _CONDITIONAL_KEYS = {
        "engine_rpm", "coolant_temp_c", "fuel_level_pct", "battery_soc_pct",
    }

    samples: list[dict] = []
    for r in rows:
        sample_row = dict(r)
        # Start from the live baseline, then overlay the sample.
        # Dynamic keys: always take the sample's value.
        # Conditional keys: take sample's value when non-None, else keep baseline.
        # Everything else: only update when the sample carries a value.
        merged = dict(baseline_dict)
        for k, v in sample_row.items():
            if k in _DYNAMIC_KEYS:
                merged[k] = v
            elif k in _CONDITIONAL_KEYS:
                if v is not None:
                    merged[k] = v
            elif v is not None:
                merged[k] = v
        # Always carry the per-sample metadata through verbatim.
        merged["case_number"]      = sample_row["case_number"]
        merged["sample_seq"]       = sample_row["sample_seq"]
        merged["seconds_relative"] = sample_row["seconds_relative"]
        merged["sample_time"]      = sample_row["sample_time"]
        merged["event_flag"]       = sample_row.get("event_flag")
        # Wheel speeds are not stored per-sample yet — derive them from the
        # main vehicle_speed_kmh on the fly so all 4 vary across the scrubber.
        v_speed = merged.get("vehicle_speed_kmh")
        if v_speed is not None:
            abs_now = sample_row.get("abs_active")
            # During ABS modulation, wheel speeds diverge slightly per wheel.
            if abs_now:
                merged["wheel_speed_fl_kmh"] = max(0, v_speed - 4.0)
                merged["wheel_speed_fr_kmh"] = max(0, v_speed - 2.5)
                merged["wheel_speed_rl_kmh"] = max(0, v_speed - 1.5)
                merged["wheel_speed_rr_kmh"] = max(0, v_speed - 3.0)
            else:
                merged["wheel_speed_fl_kmh"] = v_speed
                merged["wheel_speed_fr_kmh"] = v_speed
                merged["wheel_speed_rl_kmh"] = v_speed
                merged["wheel_speed_rr_kmh"] = v_speed
        # Transmission shafts move with engine RPM on ICE cars.
        rpm_now = merged.get("engine_rpm")
        if rpm_now is not None:
            merged["transmission_input_rpm"]  = rpm_now
            merged["transmission_output_rpm"] = max(0, rpm_now / 2.0)
        # Motor speed tracks vehicle speed on BEVs (rough 1 km/h ≈ 75 rpm).
        # Motor + inverter temperatures rise with sustained load and during the
        # crash itself, then cool down after the vehicle stops.
        if merged.get("battery_soc_pct") is not None and v_speed is not None:
            merged["motor_speed_rpm"]  = round(v_speed * 75.0, 1)
            throttle_now = merged.get("throttle_position_pct") or 0
            merged["motor_torque_nm"]  = round(throttle_now * 5.0, 1)
            t_rel = merged.get("seconds_relative") or 0
            load = (v_speed or 0) * 0.18 + throttle_now * 0.25
            if t_rel < 0:
                motor_t = 38 + load * 0.55          # warming under approach load
            elif t_rel <= 5:
                motor_t = 38 + load * 0.55 + 9.0    # spike during impact / regen dump
            else:
                cool = max(0.0, 1.0 - (t_rel - 5) / 295.0)
                motor_t = 38 + cool * 18.0          # cooling toward 38 °C
            merged["motor_temp_c"]    = round(motor_t, 1)
            merged["inverter_temp_c"] = round(motor_t - 6.0, 1)
        # Ignition state flips off after impact when the engine stops / car is wrecked.
        if merged.get("seconds_relative") is not None and merged["seconds_relative"] >= 60:
            merged["ignition_state"] = "off"
            merged["parked"] = 1
        samples.append(merged)

    events: list[dict] = []
    last_flag = None
    for s in samples:
        flag = s.get("event_flag")
        if flag and flag != last_flag and flag != "normal":
            events.append({
                "sec_relative": s["seconds_relative"],
                "sample_time": s["sample_time"],
                "tag": flag,
            })
            last_flag = flag

    impact_sample = next((s for s in samples if s["seconds_relative"] == 0), None)

    return {
        "case_number":      case_number,
        "incident":         dict(inv) if inv else None,
        "window_start":     samples[0]["sample_time"],
        "window_end":       samples[-1]["sample_time"],
        "impact_time":      impact_sample["sample_time"] if impact_sample else None,
        "sample_interval_s": 5,
        "total_samples":    len(samples),
        "events":           events,
        "samples":          samples,
    }


@router.get("/api/db/investigations/{case_number}/photos")
def list_investigation_photos(case_number: str):
    """All photos uploaded for an investigation."""
    print(f"🚦 [API HIT] /api/db/investigations/{case_number}/photos")
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    photos = cursor.execute(
        """
        SELECT id, case_number, filename, caption, photo_type, uploaded_at
        FROM investigation_photos
        WHERE case_number = ?
        ORDER BY uploaded_at
        """,
        (case_number,),
    ).fetchall()
    conn.close()
    return [dict(p) for p in photos]


# ══════════════════════════════════════════════════════════════════════════
# TELEMETRY CATEGORIES — schema introspection for the UI
# Returns the 18 raw-signal categories (GPS, IMU, OBD engine, TPMS, EV, …)
# so the Vehicle Passport + Adjuster can render labelled sections without
# the column list drifting from telemetry_seeder.py.
# ══════════════════════════════════════════════════════════════════════════

_TELEMETRY_CATEGORY_META = {
    "gps":             {"label": "GPS / Position",       "icon": "📍"},
    "imu":             {"label": "IMU — Accel & Gyro",   "icon": "🎚️"},
    "crash_event":     {"label": "Crash & Harsh Events", "icon": "💥"},
    "obd_engine":      {"label": "Engine (OBD-II)",      "icon": "⚙️"},
    "obd_fuel":        {"label": "Fuel System",          "icon": "⛽"},
    "speed":           {"label": "Vehicle & Wheel Speed","icon": "💨"},
    "emissions":       {"label": "Emissions",            "icon": "🌫️"},
    "electrical_12v":  {"label": "12 V Electrical",      "icon": "🔋"},
    "brake":           {"label": "Brake System",         "icon": "🛑"},
    "steering":        {"label": "Steering",             "icon": "🎯"},
    "transmission":    {"label": "Transmission",         "icon": "⚙️"},
    "tpms":            {"label": "TPMS (Tire Pressure)", "icon": "🛞"},
    "ev_hybrid":       {"label": "EV / Hybrid Powertrain","icon": "🔌"},
    "adas":            {"label": "ADAS / Active Safety", "icon": "🛡️"},
    "behavior":        {"label": "Driver Behaviour",     "icon": "📊"},
    "dtc":             {"label": "Diagnostic Trouble Codes", "icon": "🔧"},
    "trip":            {"label": "Trip & Odometer",      "icon": "🛣️"},
    "device":          {"label": "Blackbox Device",      "icon": "📡"},
}


@router.get("/api/db/telemetry/categories")
def get_telemetry_categories():
    """Catalogue of raw telemetry signals grouped by source.

    Each category lists the SQL column names that belong to it; the UI maps
    those onto cards labelled with a human-friendly prettifier client-side.
    The order matches the order declared in telemetry_seeder.category_index().
    """
    print("🚦 [API HIT] /api/db/telemetry/categories")
    from models.data_manager.telemetry_seeder import category_index

    cats = category_index()
    return {
        "categories": [
            {
                "key":     key,
                "label":   _TELEMETRY_CATEGORY_META.get(key, {}).get("label", key.title()),
                "icon":    _TELEMETRY_CATEGORY_META.get(key, {}).get("icon", "📡"),
                "columns": cols,
            }
            for key, cols in cats.items()
        ],
    }


# ══════════════════════════════════════════════════════════════════════════
# ESG & CIRCULAR ECONOMY — Component inventory + KPI stats
# Drives static/partials/esg_tab.html "Inventory & Ledger" sub-tab.
# ══════════════════════════════════════════════════════════════════════════

@router.get("/api/db/components")
def list_all_components(
    category: Optional[str] = None,
    status: Optional[str] = None,
    brand: Optional[str] = None,
    vehicle_vin: Optional[str] = None,
    min_wear: Optional[float] = None,
    max_wear: Optional[float] = None,
    page: int = 1,
    per_page: int = 50,
):
    """Filtered, paginated component browser feeding the ESG ledger table."""
    print(f"🚦 [API HIT] /api/db/components (cat={category}, status={status}, page={page})")
    import json as _json

    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()

    where = ["1=1"]
    params: list = []
    if category:
        where.append("c.category = ?"); params.append(category)
    if status:
        where.append("c.status = ?"); params.append(status)
    if brand:
        where.append("c.brand = ?"); params.append(brand)
    if vehicle_vin:
        where.append("c.vehicle_vin = ?"); params.append(vehicle_vin)
    if min_wear is not None:
        where.append("c.wear_percent >= ?"); params.append(min_wear)
    if max_wear is not None:
        where.append("c.wear_percent <= ?"); params.append(max_wear)

    total = cursor.execute(
        f"SELECT COUNT(*) FROM components c WHERE {' AND '.join(where)}",
        params,
    ).fetchone()[0]

    offset = (page - 1) * per_page
    rows = cursor.execute(
        f"""
        SELECT c.*, v.plate_number
        FROM components c
        LEFT JOIN vehicles v ON c.vehicle_vin = v.vin
        WHERE {' AND '.join(where)}
        ORDER BY c.category, c.wear_percent DESC
        LIMIT ? OFFSET ?
        """,
        params + [per_page, offset],
    ).fetchall()
    conn.close()

    components = []
    for r in rows:
        d = dict(r)
        if d.get("specs_json"):
            try:
                d["specs"] = _json.loads(d["specs_json"])
            except Exception:
                d["specs"] = {}
        components.append(d)
    return {"components": components, "total": total, "page": page, "per_page": per_page}


# ── Metadata for the 8 component categories (label + icon used by the UI). ──
_COMPONENT_CATEGORY_META = {
    "tire":              {"label": "Tires",            "icon": "🛞", "color": "emerald"},
    "brake_pad":         {"label": "Brake Pads",       "icon": "🛑", "color": "amber"},
    "brake_disc":        {"label": "Brake Discs",      "icon": "💿", "color": "amber"},
    "suspension_damper": {"label": "Suspension",       "icon": "🪜", "color": "slate"},
    "aux_12v_battery":   {"label": "12 V Batteries",   "icon": "🔋", "color": "yellow"},
    "engine_oil":        {"label": "Engine Oil",       "icon": "🛢️", "color": "orange"},
    "dpf":               {"label": "DPF / Particulate","icon": "🌫️", "color": "rose"},
    "ev_battery":        {"label": "EV Batteries",     "icon": "⚡", "color": "blue"},
}


@router.get("/api/db/components/stats")
def get_component_stats():
    """Aggregated stats + per-category breakdown for the ESG dashboard."""
    print("🚦 [API HIT] /api/db/components/stats")
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()

    total = cursor.execute("SELECT COUNT(*) FROM components").fetchone()[0]
    stocked = cursor.execute(
        "SELECT COUNT(*) FROM components WHERE status = 'stocked'"
    ).fetchone()[0]
    installed = cursor.execute(
        "SELECT COUNT(*) FROM components WHERE status = 'installed'"
    ).fetchone()[0]
    total_co2 = cursor.execute(
        "SELECT COALESCE(SUM(co2_saved_kg), 0) FROM components WHERE status != 'installed'"
    ).fetchone()[0]
    total_value = cursor.execute(
        "SELECT COALESCE(SUM(recovery_value_eur), 0) FROM components WHERE status != 'installed'"
    ).fetchone()[0]

    # Per-category breakdown — counts by status + recovery sums for stocked.
    cat_rows = cursor.execute("""
        SELECT category,
               COUNT(*)                                              AS total,
               SUM(CASE WHEN status='installed' THEN 1 ELSE 0 END)   AS installed,
               SUM(CASE WHEN status='stocked'   THEN 1 ELSE 0 END)   AS stocked,
               COALESCE(SUM(CASE WHEN status!='installed' THEN recovery_value_eur ELSE 0 END), 0) AS value_eur,
               COALESCE(SUM(CASE WHEN status!='installed' THEN co2_saved_kg       ELSE 0 END), 0) AS co2_kg,
               AVG(wear_percent)                                     AS avg_wear
        FROM components
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    categories = []
    by_category = {}
    for r in cat_rows:
        key = r["category"]
        meta = _COMPONENT_CATEGORY_META.get(key, {})
        categories.append({
            "key":       key,
            "label":     meta.get("label", key.replace("_", " ").title()),
            "icon":      meta.get("icon", "📦"),
            "color":     meta.get("color", "slate"),
            "total":     r["total"],
            "installed": r["installed"] or 0,
            "stocked":   r["stocked"] or 0,
            "value_eur": round(r["value_eur"] or 0, 2),
            "co2_kg":    round(r["co2_kg"] or 0, 1),
            "avg_wear":  round(r["avg_wear"] or 0, 1),
        })
        by_category[key] = r["total"]
    conn.close()

    return {
        "total_components": total,
        "stocked": stocked,
        "installed": installed,
        "total_co2_saved_kg": round(total_co2, 1),
        "total_recovery_value_eur": round(total_value, 2),
        "by_category": by_category,
        "categories": categories,
    }


# ══════════════════════════════════════════════════════════════════════════
# (Investigation photo upload — kept below the ESG block for grouping)
# ══════════════════════════════════════════════════════════════════════════

@router.post("/api/db/investigations/{case_number}/photos")
async def upload_investigation_photo(case_number: str, request: Request):
    """Upload a damage photo (multipart form or base64 JSON body)."""
    import base64
    print(f"🚦 [API HIT] POST /api/db/investigations/{case_number}/photos")

    content_type = request.headers.get("content-type", "")
    img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                           "static", "img", "investigations"))
    os.makedirs(img_dir, exist_ok=True)

    if "multipart" in content_type:
        form = await request.form()
        file = form.get("file")
        caption = form.get("caption", "Uploaded damage photo")
        photo_type = form.get("photo_type", "damage")
        if not file:
            return {"error": "No file provided"}
        ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
        filename = f"{case_number}_{uuid.uuid4().hex[:8]}.{ext}"
        with open(os.path.join(img_dir, filename), "wb") as f:
            f.write(await file.read())
    else:
        body = await request.json()
        caption = body.get("caption", "Uploaded damage photo")
        photo_type = body.get("photo_type", "damage")
        image_data = body.get("image_data", "")
        if not image_data:
            return {"error": "No image_data provided"}
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]
        filename = f"{case_number}_{uuid.uuid4().hex[:8]}.png"
        with open(os.path.join(img_dir, filename), "wb") as f:
            f.write(base64.b64decode(image_data))

    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO investigation_photos (case_number, filename, caption, photo_type) "
        "VALUES (?, ?, ?, ?)",
        (case_number, filename, caption, photo_type),
    )
    conn.commit()
    conn.close()
    return {"success": True, "filename": filename, "caption": caption}