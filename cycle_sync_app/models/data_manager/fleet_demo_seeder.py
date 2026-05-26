"""
Fleet demo seeder — shrink the 3,480-row mock fleet down to ten hand-tuned
vehicles, then populate every telemetry signal for each one with realistic
values driven by a per-vehicle "driver profile".

The ten survivors are:
  • the 5 VINs already linked to investigations  (kept intact)
  • 1 of each remaining car_model + 1 spare      (5 more, picked deterministically)

Every survivor lands in vehicle_telemetry with all OBD-II + blackbox
columns populated according to its profile (safe / eco / aggressive /
charging / collision / old-diesel-with-DTCs / aggressive-with-tpms-warning).

Idempotent: a marker row in `_seeder_state` prevents a second cull on later
boots. Delete the marker (or the table) to re-run.
"""
import json
import math
import random
import sqlite3
from datetime import datetime, timedelta

from .database_manager import DatabaseManager


_MARKER_KEY = "fleet_demo_v1"


# ──────────────────────────────────────────────────────────────────────────
# 1. THE TEN SURVIVORS
# ──────────────────────────────────────────────────────────────────────────
# 5 protected VINs (linked to investigations seeded earlier). Their
# blackbox state must reflect "post-incident" — locked, parked, event-flag set.
_PROTECTED_VINS: dict[str, dict] = {
    "SIMD9486C283C8C4D": {  # Maserati Grecale Folgore — Antonio Moretti
        "profile":      "aggressive",
        "incident":     "CASE-2024-00142",
        "post_crash":   True,
    },
    "SIME29F07EE506845": {  # Tesla Model 3 — Maria Russo
        "profile":      "safe_eco",
        "incident":     "CASE-2024-00287",
        "post_crash":   True,
    },
    "SIMB48161B11D1E43": {  # Fiat 500e — Nicola Caruso
        "profile":      "aggressive",
        "incident":     "CASE-2024-00391",
        "post_crash":   True,
    },
    "SIMF69EB9641D4B45": {  # Volkswagen Golf — Aurora Martini
        "profile":      "average",
        "incident":     "CASE-2025-00012",
        "post_crash":   False,  # resolved case, vehicle back on road
    },
    "SIMFAB56F374C874B": {  # BMW X5 — Monica Rinaldi
        "profile":      "average",
        "incident":     "CASE-2025-00045",
        "post_crash":   True,
    },
}

# 5 extra slots — picked deterministically per car_model so re-runs are stable.
# (manufacturer, model, profile, label_for_logs)
_EXTRA_SLOTS: list[tuple[str, str, str, str]] = [
    ("Toyota",     "Yaris",            "eco_hybrid_commuter",  "Toyota Yaris hybrid — eco driver"),
    ("Maserati",   "Grecale Folgore",  "charging_bev",         "Maserati Grecale Folgore #2 — charging"),
    ("Tesla",      "Model 3",          "highway_commuter",     "Tesla Model 3 #2 — highway commuter"),
    ("Volkswagen", "Golf",             "old_diesel_dtc",       "VW Golf #2 — high-mileage diesel with DTCs"),
    ("BMW",        "X5",               "aggressive_tpms",      "BMW X5 #2 — aggressive driver, TPMS warning"),
]


# ──────────────────────────────────────────────────────────────────────────
# 2. POWERTRAIN BASELINES
# ──────────────────────────────────────────────────────────────────────────
# Snapshot of a "moving normally" reading for each powertrain. Profile
# overrides layer on top of these.

_BEV_BASE = {
    # ICE-only signals → NULL (no engine, no fuel, no aftertreatment)
    "engine_rpm": None, "engine_load_pct": None, "engine_runtime_s": None,
    "coolant_temp_c": None, "intake_air_temp_c": None, "maf_g_per_s": None,
    "map_kpa": None, "throttle_position_pct": None, "ignition_timing_adv_deg": None,
    "fuel_level_pct": None, "fuel_pressure_kpa": None, "fuel_rail_pressure_kpa": None,
    "short_term_fuel_trim_pct": None, "long_term_fuel_trim_pct": None,
    "commanded_afr": None, "fuel_type": "electric",
    "o2_voltage_b1s1": None, "o2_voltage_b1s2": None, "catalyst_temp_b1s1_c": None,
    "egr_commanded_pct": None, "egr_actual_pct": None, "evap_system_pressure_pa": None,
    "nox_ppm": None,

    # EV signals populated
    "battery_soc_pct": 64.0, "battery_soh_pct": 96.0,
    "battery_pack_voltage_v": 397.6, "battery_pack_current_a": -18.4,  # mild regen
    "battery_temp_min_c": 22.0, "battery_temp_max_c": 28.0,
    "battery_cell_v_min": 3.71, "battery_cell_v_max": 3.78,
    "battery_energy_kwh": 58.2,
    "motor_speed_rpm": 4200.0, "motor_torque_nm": 210.0,
    "motor_temp_c": 42.0, "inverter_temp_c": 56.0,
    "regen_braking_pct": 38.0,
    "charge_status": "driving", "charging_power_kw": 0.0,
    "estimated_range_km": 312.0,
}

_ICE_BASE = {
    # EV-only signals → NULL
    "battery_soc_pct": None, "battery_soh_pct": None,
    "battery_pack_voltage_v": None, "battery_pack_current_a": None,
    "battery_temp_min_c": None, "battery_temp_max_c": None,
    "battery_cell_v_min": None, "battery_cell_v_max": None,
    "battery_energy_kwh": None,
    "motor_speed_rpm": None, "motor_torque_nm": None, "motor_temp_c": None,
    "inverter_temp_c": None, "regen_braking_pct": None,
    "charge_status": None, "charging_power_kw": None, "estimated_range_km": None,

    # ICE signals populated (typical petrol cruising at ~70 km/h)
    "engine_rpm": 2200.0, "engine_load_pct": 38.0, "engine_runtime_s": 1840,
    "coolant_temp_c": 91.0, "intake_air_temp_c": 28.0, "maf_g_per_s": 11.4,
    "map_kpa": 62.0, "throttle_position_pct": 22.0, "ignition_timing_adv_deg": 16.0,
    "fuel_level_pct": 64.0, "fuel_pressure_kpa": 320.0, "fuel_rail_pressure_kpa": 3850.0,
    "short_term_fuel_trim_pct": 1.2, "long_term_fuel_trim_pct": -0.8,
    "commanded_afr": 14.6, "fuel_type": "petrol",
    "o2_voltage_b1s1": 0.85, "o2_voltage_b1s2": 0.68,
    "catalyst_temp_b1s1_c": 612.0,
    "egr_commanded_pct": 8.2, "egr_actual_pct": 7.9,
    "evap_system_pressure_pa": -22.0, "nox_ppm": None,
}

_DIESEL_OVERLAY = {
    "fuel_type": "diesel", "commanded_afr": 21.0, "nox_ppm": 38.0,
    "fuel_rail_pressure_kpa": 18000.0,  # diesel common rail is far higher
}

_HYBRID_BASE = {
    # Both engine and motor active (split powertrain)
    "engine_rpm": 1800.0, "engine_load_pct": 22.0, "engine_runtime_s": 920,
    "coolant_temp_c": 89.0, "intake_air_temp_c": 26.0, "maf_g_per_s": 7.2,
    "map_kpa": 48.0, "throttle_position_pct": 14.0, "ignition_timing_adv_deg": 22.0,
    "fuel_level_pct": 72.0, "fuel_pressure_kpa": 280.0, "fuel_rail_pressure_kpa": 3600.0,
    "short_term_fuel_trim_pct": 0.4, "long_term_fuel_trim_pct": 0.1,
    "commanded_afr": 14.7, "fuel_type": "hybrid",
    "o2_voltage_b1s1": 0.78, "o2_voltage_b1s2": 0.65,
    "catalyst_temp_b1s1_c": 540.0,
    "egr_commanded_pct": 5.5, "egr_actual_pct": 5.2,
    "evap_system_pressure_pa": -18.0, "nox_ppm": None,

    # Small traction battery (Yaris-class)
    "battery_soc_pct": 58.0, "battery_soh_pct": 96.0,
    "battery_pack_voltage_v": 245.0, "battery_pack_current_a": 4.2,
    "battery_temp_min_c": 28.0, "battery_temp_max_c": 32.0,
    "battery_cell_v_min": 3.85, "battery_cell_v_max": 3.92,
    "battery_energy_kwh": 1.3,
    "motor_speed_rpm": 1200.0, "motor_torque_nm": 80.0,
    "motor_temp_c": 38.0, "inverter_temp_c": 42.0,
    "regen_braking_pct": 25.0,
    "charge_status": "driving", "charging_power_kw": 0.0,
    "estimated_range_km": 580.0,  # ICE + EV combined
}


# ──────────────────────────────────────────────────────────────────────────
# 3. DRIVER PROFILES — sharp differences between drivers
# ──────────────────────────────────────────────────────────────────────────
_PROFILES = {
    # 88-score safe eco driver — short urban + long highway, smooth inputs
    "safe_eco": {
        "driving_score": 88, "safety_score": 92, "eco_score": 88, "smoothness_score": 91,
        "hard_brake_count": 8, "hard_accel_count": 5, "hard_cornering_count": 3,
        "speeding_events_count": 2, "harsh_event_count_24h": 0, "idle_time_s": 1800,
        "night_driving_pct": 8.0, "highway_driving_pct": 35.0, "urban_driving_pct": 57.0,
        "abs_activations_count": 2, "esc_interventions_count": 1, "aeb_activations_count": 0,
        "lane_departure_warnings_count": 4, "forward_collision_warnings_count": 1,
        "traction_control_interventions_count": 3,
        "blackbox_event_type": "normal", "event_max_g": 0.6, "impact_severity": "none",
        "avg_speed_kmh": 38.0, "max_speed_kmh": 128.0,
    },
    # 38-score aggressive — frequent hard inputs, ABS/ESC firing often
    "aggressive": {
        "driving_score": 38, "safety_score": 35, "eco_score": 28, "smoothness_score": 32,
        "hard_brake_count": 142, "hard_accel_count": 188, "hard_cornering_count": 96,
        "speeding_events_count": 67, "harsh_event_count_24h": 7, "idle_time_s": 5400,
        "night_driving_pct": 28.0, "highway_driving_pct": 55.0, "urban_driving_pct": 17.0,
        "abs_activations_count": 38, "esc_interventions_count": 22, "aeb_activations_count": 4,
        "lane_departure_warnings_count": 78, "forward_collision_warnings_count": 19,
        "traction_control_interventions_count": 45,
        "blackbox_event_type": "hard_brake", "event_max_g": 1.6, "impact_severity": "low",
        "avg_speed_kmh": 58.0, "max_speed_kmh": 184.0,
    },
    # 62-score average — balanced inputs
    "average": {
        "driving_score": 62, "safety_score": 58, "eco_score": 60, "smoothness_score": 65,
        "hard_brake_count": 42, "hard_accel_count": 38, "hard_cornering_count": 25,
        "speeding_events_count": 14, "harsh_event_count_24h": 1, "idle_time_s": 3200,
        "night_driving_pct": 15.0, "highway_driving_pct": 45.0, "urban_driving_pct": 40.0,
        "abs_activations_count": 8, "esc_interventions_count": 4, "aeb_activations_count": 1,
        "lane_departure_warnings_count": 18, "forward_collision_warnings_count": 5,
        "traction_control_interventions_count": 12,
        "blackbox_event_type": "normal", "event_max_g": 0.9, "impact_severity": "none",
        "avg_speed_kmh": 48.0, "max_speed_kmh": 146.0,
    },
    # Toyota Yaris hybrid — gentlest profile, mostly urban
    "eco_hybrid_commuter": {
        "driving_score": 92, "safety_score": 95, "eco_score": 96, "smoothness_score": 94,
        "hard_brake_count": 3, "hard_accel_count": 2, "hard_cornering_count": 1,
        "speeding_events_count": 0, "harsh_event_count_24h": 0, "idle_time_s": 2400,
        "night_driving_pct": 5.0, "highway_driving_pct": 18.0, "urban_driving_pct": 77.0,
        "abs_activations_count": 1, "esc_interventions_count": 0, "aeb_activations_count": 0,
        "lane_departure_warnings_count": 2, "forward_collision_warnings_count": 0,
        "traction_control_interventions_count": 1,
        "blackbox_event_type": "normal", "event_max_g": 0.4, "impact_severity": "none",
        "avg_speed_kmh": 28.0, "max_speed_kmh": 96.0,
        "engine_rpm": 980.0, "engine_load_pct": 12.0, "throttle_position_pct": 6.0,
    },
    # Maserati at supercharger — stationary, drawing 87 kW
    "charging_bev": {
        "driving_score": 72, "safety_score": 75, "eco_score": 82, "smoothness_score": 78,
        "hard_brake_count": 18, "hard_accel_count": 22, "hard_cornering_count": 12,
        "speeding_events_count": 8, "harsh_event_count_24h": 0, "idle_time_s": 0,
        "night_driving_pct": 12.0, "highway_driving_pct": 62.0, "urban_driving_pct": 26.0,
        "abs_activations_count": 4, "esc_interventions_count": 2, "aeb_activations_count": 0,
        "lane_departure_warnings_count": 8, "forward_collision_warnings_count": 2,
        "traction_control_interventions_count": 5,
        "blackbox_event_type": "normal", "event_max_g": 0.3, "impact_severity": "none",
        "avg_speed_kmh": 0.0, "max_speed_kmh": 168.0,
        # Charging-specific overrides
        "charge_status": "charging_dc", "charging_power_kw": 87.4,
        "battery_soc_pct": 42.0, "battery_pack_current_a": 220.0,
        "battery_temp_min_c": 34.0, "battery_temp_max_c": 41.0,
        "estimated_range_km": 168.0,
        "motor_speed_rpm": 0.0, "motor_torque_nm": 0.0,
        "regen_braking_pct": 0.0,
        "vehicle_speed_kmh": 0.0, "gps_speed_kmh": 0.0,
        "wheel_speed_fl_kmh": 0.0, "wheel_speed_fr_kmh": 0.0,
        "wheel_speed_rl_kmh": 0.0, "wheel_speed_rr_kmh": 0.0,
        "parked": 1, "ignition_state": "off", "gear_position": "P",
        "transmission_input_rpm": 0.0, "transmission_output_rpm": 0.0,
    },
    # Tesla on the autostrada — high distance, mostly highway
    "highway_commuter": {
        "driving_score": 76, "safety_score": 74, "eco_score": 80, "smoothness_score": 82,
        "hard_brake_count": 22, "hard_accel_count": 18, "hard_cornering_count": 8,
        "speeding_events_count": 28, "harsh_event_count_24h": 0, "idle_time_s": 800,
        "night_driving_pct": 12.0, "highway_driving_pct": 78.0, "urban_driving_pct": 10.0,
        "abs_activations_count": 4, "esc_interventions_count": 1, "aeb_activations_count": 0,
        "lane_departure_warnings_count": 24, "forward_collision_warnings_count": 6,
        "traction_control_interventions_count": 3,
        "blackbox_event_type": "normal", "event_max_g": 0.5, "impact_severity": "none",
        "avg_speed_kmh": 92.0, "max_speed_kmh": 154.0,
        "vehicle_speed_kmh": 118.0, "gps_speed_kmh": 118.0,
        "wheel_speed_fl_kmh": 118.0, "wheel_speed_fr_kmh": 118.0,
        "wheel_speed_rl_kmh": 118.0, "wheel_speed_rr_kmh": 118.0,
        "motor_speed_rpm": 8600.0, "motor_torque_nm": 95.0,
        "battery_soc_pct": 58.0, "estimated_range_km": 268.0,
    },
    # Old VW Golf diesel with MIL on
    "old_diesel_dtc": {
        "driving_score": 55, "safety_score": 50, "eco_score": 45, "smoothness_score": 60,
        "hard_brake_count": 64, "hard_accel_count": 48, "hard_cornering_count": 32,
        "speeding_events_count": 22, "harsh_event_count_24h": 1, "idle_time_s": 6800,
        "night_driving_pct": 18.0, "highway_driving_pct": 52.0, "urban_driving_pct": 30.0,
        "abs_activations_count": 14, "esc_interventions_count": 6, "aeb_activations_count": 0,
        "lane_departure_warnings_count": 9, "forward_collision_warnings_count": 3,
        "traction_control_interventions_count": 8,
        "blackbox_event_type": "normal", "event_max_g": 0.7, "impact_severity": "none",
        "avg_speed_kmh": 52.0, "max_speed_kmh": 168.0,
        # DTC overrides — check engine on
        "mil_active": 1, "dtc_count": 2,
        "dtc_codes_json": json.dumps(["P0420", "P0171"]),
        "pending_dtc_codes_json": json.dumps(["P0300"]),
        "distance_with_mil_on_km": 1240.0, "distance_since_codes_cleared_km": 8400.0,
        "freeze_frame_json": json.dumps({
            "code": "P0420", "rpm": 2400, "coolant_c": 94, "load_pct": 68,
            "speed_kmh": 62, "fuel_trim_lt_pct": 8.4,
        }),
        # Running slightly hot, slight rich condition
        "coolant_temp_c": 96.0, "long_term_fuel_trim_pct": 8.4,
        "catalyst_temp_b1s1_c": 460.0,  # cat efficiency degraded
    },
    # BMW X5 aggressive driver with a slow leak on front-left
    "aggressive_tpms": {
        "driving_score": 42, "safety_score": 40, "eco_score": 38, "smoothness_score": 44,
        "hard_brake_count": 108, "hard_accel_count": 142, "hard_cornering_count": 72,
        "speeding_events_count": 54, "harsh_event_count_24h": 5, "idle_time_s": 4200,
        "night_driving_pct": 24.0, "highway_driving_pct": 60.0, "urban_driving_pct": 16.0,
        "abs_activations_count": 28, "esc_interventions_count": 18, "aeb_activations_count": 2,
        "lane_departure_warnings_count": 54, "forward_collision_warnings_count": 12,
        "traction_control_interventions_count": 32,
        "blackbox_event_type": "hard_cornering", "event_max_g": 1.4, "impact_severity": "low",
        "avg_speed_kmh": 62.0, "max_speed_kmh": 196.0,
        # TPMS warning overrides
        "tpms_fl_bar": 1.7,            # below 1.8 → red
        "tpms_fl_temp_c": 48.0,         # heating up from underinflation
    },
}


# ──────────────────────────────────────────────────────────────────────────
# 4. COMMON / BLACKBOX-NATIVE FIELDS
# ──────────────────────────────────────────────────────────────────────────
def _common(vehicle_info: dict) -> dict:
    """Fields shared by every vehicle — GPS, IMU, TPMS healthy, device, etc."""
    vin = vehicle_info["vin"]
    lat = (vehicle_info.get("lat") or 41.9) + random.uniform(-0.0015, 0.0015)
    lon = (vehicle_info.get("lon") or 12.5) + random.uniform(-0.0015, 0.0015)
    odo = vehicle_info.get("odometer") or 50_000
    return {
        # GPS
        "gps_lat": lat, "gps_lon": lon,
        "gps_altitude_m": float(random.randint(20, 280)),
        "gps_heading_deg": float(random.randint(0, 359)),
        "gps_speed_kmh": 42.0, "gps_hdop": 0.8,
        "gps_satellites": 12, "gps_fix_quality": "3D",

        # IMU — gentle cruise
        "accel_x_g": 0.05, "accel_y_g": 0.02, "accel_z_g": 0.98,
        "accel_total_g": round(math.sqrt(0.05**2 + 0.02**2 + 0.98**2), 3),
        "gyro_roll_deg_s": 0.5, "gyro_pitch_deg_s": 0.3, "gyro_yaw_deg_s": 1.2,
        "tilt_angle_deg": 0.4,

        # Crash defaults (event-overrides applied later)
        "abs_active": 0, "esc_active": 0,
        "last_event_timestamp": None,

        # TPMS healthy (overridden by tpms_low / aggressive_tpms profiles)
        "tpms_fl_bar": 2.3, "tpms_fr_bar": 2.3, "tpms_rl_bar": 2.3, "tpms_rr_bar": 2.3,
        "tpms_fl_temp_c": 32.0, "tpms_fr_temp_c": 33.0,
        "tpms_rl_temp_c": 34.0, "tpms_rr_temp_c": 33.0,

        # 12 V electrical
        "control_module_voltage_v": 14.2, "battery_voltage_v": 12.6,
        "ambient_air_temp_c": 18.0,

        # Brake / steering / transmission
        "brake_pressure_bar": 0.5, "brake_pedal_pct": 0.0,
        "steering_angle_deg": 2.0, "steering_rate_deg_s": 0.4,
        "transmission_fluid_temp_c": 78.0, "gear_position": "D",
        "transmission_input_rpm": 2200.0, "transmission_output_rpm": 1100.0,

        # Speed (overridable)
        "vehicle_speed_kmh": 42.0, "avg_speed_kmh": 38.0, "max_speed_kmh": 132.0,
        "wheel_speed_fl_kmh": 42.0, "wheel_speed_fr_kmh": 42.0,
        "wheel_speed_rl_kmh": 42.0, "wheel_speed_rr_kmh": 42.0,

        # Trip / device
        "trip_distance_km": 12.4, "trip_duration_s": 1140,
        "total_trips": random.randint(800, 2400),
        "total_distance_km": float(odo),
        "ignition_state": "run", "parked": 0,
        "gsm_signal_dbm": -76, "blackbox_firmware_version": "VT-2.4.1",
        "blackbox_device_id": f"BB-{vin[3:11]}", "blackbox_battery_pct": 92.0,

        # DTC defaults (clean)
        "mil_active": 0, "dtc_count": 0,
        "dtc_codes_json": json.dumps([]),
        "pending_dtc_codes_json": json.dumps([]),
        "distance_with_mil_on_km": 0.0,
        "distance_since_codes_cleared_km": float(random.randint(4000, 22000)),
        "freeze_frame_json": None,

        # Event defaults (overridden by collision overlays)
        "event_max_g": 0.6, "impact_severity": "none",
        "blackbox_event_type": "normal",
        "current_odometer_km": int(odo),
        "driving_score": 62,
        "last_sync_timestamp": datetime.now().isoformat(timespec="seconds"),
    }


# ──────────────────────────────────────────────────────────────────────────
# 5. INVESTIGATION OVERLAY (post-crash state)
# ──────────────────────────────────────────────────────────────────────────
def _post_crash_overlay(investigation_row: dict) -> dict:
    """Telemetry snapshot for a vehicle that *just* had an incident."""
    inc = investigation_row
    g_max = inc.get("g_force_max") or 3.0
    severity = ("critical" if g_max >= 5.5
                else "high"     if g_max >= 4.0
                else "medium"   if g_max >= 2.5
                else "low")
    event_type_map = {
        "collision":   "collision_major",
        "rear_end":    "collision_minor" if g_max < 4.0 else "collision_major",
        "side_impact": "collision_major",
        "rollover":    "rollover",
        "pedestrian":  "collision_minor",
    }
    return {
        "blackbox_event_type": event_type_map.get(inc.get("incident_type"), "collision_minor"),
        "event_max_g": float(g_max),
        "impact_severity": severity,
        "last_event_timestamp": inc.get("incident_date"),
        "abs_active": 1 if inc.get("abs_triggered") else 0,
        "esc_active": 1,
        "parked": 1, "ignition_state": "off",
        "vehicle_speed_kmh": 0.0, "gps_speed_kmh": 0.0,
        "wheel_speed_fl_kmh": 0.0, "wheel_speed_fr_kmh": 0.0,
        "wheel_speed_rl_kmh": 0.0, "wheel_speed_rr_kmh": 0.0,
        "engine_rpm": 0.0 if inc else None,
        "gear_position": "P",
        "accel_x_g": 0.0, "accel_y_g": 0.0, "accel_z_g": 1.0,
        "accel_total_g": 1.0,
    }


# ──────────────────────────────────────────────────────────────────────────
# 6. SEEDER PLUMBING
# ──────────────────────────────────────────────────────────────────────────
def _ensure_marker_table(cursor):
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS _seeder_state ("
        " key TEXT PRIMARY KEY, value TEXT, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )


def _marker_set(cursor) -> bool:
    row = cursor.execute(
        "SELECT 1 FROM _seeder_state WHERE key=?", (_MARKER_KEY,)
    ).fetchone()
    return row is not None


def _set_marker(cursor):
    cursor.execute(
        "INSERT OR REPLACE INTO _seeder_state (key, value) VALUES (?, ?)",
        (_MARKER_KEY, "done"),
    )


def _pick_extra_vins(cursor, exclude: set[str]) -> list[tuple[str, str]]:
    """Return [(vin, profile_name)] for the 5 extra (non-incident) vehicles."""
    out = []
    used = set(exclude)
    for mfr, model, profile, _label in _EXTRA_SLOTS:
        row = cursor.execute(
            """
            SELECT v.vin FROM vehicles v
            JOIN car_models cm ON v.model_id = cm.id
            WHERE cm.manufacturer = ? AND cm.model_name = ?
              AND v.vin NOT IN ({})
            ORDER BY v.vin
            LIMIT 1
            """.format(",".join(["?"] * len(used)) if used else "''"),
            (mfr, model, *used),
        ).fetchone()
        if row:
            out.append((row[0], profile))
            used.add(row[0])
    return out


def _vehicle_info(cursor, vin: str) -> dict:
    """Pull the snapshot of static fields we need for telemetry generation."""
    row = cursor.execute(
        """
        SELECT v.vin, v.lat, v.lon, v.driver_name, vt.current_odometer_km,
               cm.manufacturer, cm.model_name, cm.powertrain
        FROM vehicles v
        JOIN car_models cm ON v.model_id = cm.id
        LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
        WHERE v.vin = ?
        """,
        (vin,),
    ).fetchone()
    if not row:
        return {}
    return {
        "vin": row[0], "lat": row[1], "lon": row[2], "driver_name": row[3],
        "odometer": row[4] or 50_000,
        "manufacturer": row[5], "model": row[6], "powertrain": row[7],
    }


def _investigation_for(cursor, vin: str) -> dict | None:
    row = cursor.execute(
        """
        SELECT case_number, incident_type, incident_date,
               speed_at_impact, g_force_max, g_force_lateral,
               abs_triggered, airbag_deployed
        FROM investigations WHERE vehicle_vin = ?
        LIMIT 1
        """,
        (vin,),
    ).fetchone()
    if not row:
        return None
    return {
        "case_number": row[0], "incident_type": row[1], "incident_date": row[2],
        "speed_at_impact": row[3], "g_force_max": row[4], "g_force_lateral": row[5],
        "abs_triggered": row[6], "airbag_deployed": row[7],
    }


def _powertrain_base(powertrain: str) -> dict:
    pt = (powertrain or "").upper()
    if pt == "BEV":     return dict(_BEV_BASE)
    if pt == "HYBRID":  return dict(_HYBRID_BASE)
    base = dict(_ICE_BASE)
    return base  # Diesel overlay applied per-vehicle below


def _build_row(vehicle_info: dict, profile_name: str,
               investigation: dict | None, post_crash: bool) -> dict:
    base = _powertrain_base(vehicle_info["powertrain"])
    # Diesel overlay only for the high-mileage VW Golf profile.
    if profile_name == "old_diesel_dtc":
        base.update(_DIESEL_OVERLAY)

    common = _common(vehicle_info)
    profile = _PROFILES.get(profile_name, {})

    row = {**base, **common, **profile}
    if investigation and post_crash:
        row.update(_post_crash_overlay(investigation))
    return row


def _apply_telemetry(cursor, vin: str, data: dict):
    """UPDATE vehicle_telemetry with every column that actually exists."""
    valid = {r[1] for r in cursor.execute(
        "PRAGMA table_info(vehicle_telemetry)"
    ).fetchall()}
    keys = [k for k in data if k in valid and k != "vin"]
    if not keys:
        return
    set_clause = ", ".join(f"{k}=?" for k in keys)
    values = [data[k] for k in keys] + [vin]
    cursor.execute(
        f"UPDATE vehicle_telemetry SET {set_clause} WHERE vin=?", values
    )


def _delete_non_survivors(cursor, survivors: list[str]):
    """Cull every vehicle NOT in `survivors` and its dependent rows."""
    placeholders = ",".join("?" * len(survivors))
    # child tables first so we never leave orphans even on FK-off DBs
    cursor.execute(
        f"DELETE FROM vehicle_telemetry WHERE vin NOT IN ({placeholders})",
        survivors,
    )
    cursor.execute(
        f"DELETE FROM components WHERE vehicle_vin NOT IN ({placeholders})",
        survivors,
    )
    cursor.execute(
        f"DELETE FROM mounted_tires WHERE vin NOT IN ({placeholders})",
        survivors,
    )
    cursor.execute(
        f"DELETE FROM maintenance_events WHERE vehicle_vin NOT IN ({placeholders})",
        survivors,
    )
    try:
        cursor.execute(
            f"DELETE FROM driver_vehicles WHERE vin NOT IN ({placeholders})",
            survivors,
        )
    except sqlite3.OperationalError:
        pass  # table may be missing; harmless

    cursor.execute(
        f"DELETE FROM vehicles WHERE vin NOT IN ({placeholders})",
        survivors,
    )


# ──────────────────────────────────────────────────────────────────────────
# 6b. RELINK THE DEMO DRIVER
#
# The cull deletes every `driver_vehicles` row whose VIN isn't a survivor,
# which leaves the consumer driver app showing an empty garage. We re-link
# the seeded `driver_accounts` row(s) to a hand-picked pair of survivor
# VINs so /driver always has something to render after a fresh boot.
#
# Pinned VIN: the Maserati Grecale Folgore (Antonio Moretti's BEV) — its
# driver_name on `vehicles` already matches the driver_account surname.
# ──────────────────────────────────────────────────────────────────────────
_DEMO_DRIVER_GARAGE = [
    "SIMD9486C283C8C4D",   # Maserati Grecale Folgore (BEV, incident-linked)
    "SIM00E85293920545",   # Tesla Model 3            (BEV, low-km daily)
]
_DEMO_DRIVER_PINNED = "SIMD9486C283C8C4D"


def _relink_demo_driver(cursor, survivors: list[str]):
    """Ensure every seeded driver_account has at least one surviving VIN in
    its garage + a valid `pinned_vin`. Safe on every boot."""
    survivor_set = set(survivors)
    garage = [v for v in _DEMO_DRIVER_GARAGE if v in survivor_set]
    if not garage:
        # Fallback: pin the highest-VSI survivor (deterministic order).
        garage = survivors[:2]
    pinned = _DEMO_DRIVER_PINNED if _DEMO_DRIVER_PINNED in survivor_set else garage[0]

    drivers = cursor.execute("SELECT id FROM driver_accounts").fetchall()
    for (driver_id,) in drivers:
        for vin in garage:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO driver_vehicles (driver_id, vin) VALUES (?, ?)",
                    (driver_id, vin),
                )
            except sqlite3.OperationalError:
                pass  # table missing on extremely fresh DBs — harmless
        # Repoint pinned_vin if it currently points at a culled VIN.
        row = cursor.execute(
            "SELECT pinned_vin FROM driver_accounts WHERE id=?", (driver_id,)
        ).fetchone()
        if not row or row[0] not in survivor_set:
            cursor.execute(
                "UPDATE driver_accounts SET pinned_vin=? WHERE id=?",
                (pinned, driver_id),
            )


# ──────────────────────────────────────────────────────────────────────────
# 7. ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────
def migrate_and_seed():
    """Cull the fleet down to 10 hand-tuned vehicles + populate full telemetry.

    Skipped on later boots once the `fleet_demo_v1` marker is set. Delete the
    row from `_seeder_state` to force a re-run.
    """
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()

    _ensure_marker_table(cursor)
    if _marker_set(cursor):
        conn.close()
        return  # already curated

    random.seed(42)  # deterministic jitter so reruns produce identical demo data

    # 1. Compose the list of 10 survivor VINs.
    protected = list(_PROTECTED_VINS.keys())
    extras = _pick_extra_vins(cursor, set(protected))
    extras_by_vin = {vin: prof for vin, prof in extras}
    survivors = protected + [vin for vin, _ in extras]

    if len(survivors) < 6:  # not enough seed data to do anything sensible
        conn.close()
        return

    # 2. Cull everything else.
    pre_count = cursor.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
    _delete_non_survivors(cursor, survivors)
    conn.commit()
    post_count = cursor.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
    print(f"🚙 fleet_demo_seeder: culled fleet "
          f"{pre_count} → {post_count} vehicles.")

    # 3. Populate full telemetry for each survivor.
    for vin in survivors:
        info = _vehicle_info(cursor, vin)
        if not info:
            continue
        if vin in _PROTECTED_VINS:
            profile = _PROTECTED_VINS[vin]["profile"]
            post_crash = _PROTECTED_VINS[vin].get("post_crash", True)
            inv = _investigation_for(cursor, vin)
        else:
            profile = extras_by_vin[vin]
            post_crash = False
            inv = None

        row = _build_row(info, profile, inv, post_crash)
        _apply_telemetry(cursor, vin, row)

    # 3b. Re-link the demo driver to surviving vehicles. The cull above wipes
    # every driver_vehicles row whose VIN isn't a survivor; without this step
    # the consumer-facing driver app shows an empty garage on a fresh boot.
    _relink_demo_driver(cursor, survivors)

    # 4. Mark done.
    _set_marker(cursor)
    conn.commit()
    conn.close()

    print(f"📊 fleet_demo_seeder: populated full telemetry for "
          f"{len(survivors)} vehicles "
          f"({len(protected)} incident-linked + {len(extras)} diversified).")


if __name__ == "__main__":
    migrate_and_seed()
