"""
Telemetry schema seeder — extends `vehicle_telemetry` with the full raw-signal
surface a UNIPOL-style insurance blackbox + an OBD-II / ECU connection can
emit, grouped into 18 categories.

This file ONLY changes the schema (ALTER TABLE ADD COLUMN, idempotent).
Population is intentionally NOT done here — wait for the user's next
instruction on how each category should be filled.

Run on every boot via the startup hook in website/main.py.
"""
import sqlite3

from .database_manager import DatabaseManager


# ────────────────────────────────────────────────────────────────────────────
# Column catalogue — grouped by source/category.
# Each entry is (column_name, sqlite_type, comment).
# Types: REAL=float sensor, INTEGER=count/boolean, TEXT=code/state/JSON,
#        DATETIME=timestamp.
# SQLite forbids non-constant defaults on ALTER TABLE ADD COLUMN, so every
# new column lands NULLable.
# ────────────────────────────────────────────────────────────────────────────

_TELEMETRY_COLUMNS: list[tuple[str, str, str]] = [

    # ── A. GPS / Position (blackbox GNSS) ──────────────────────────────────
    ("gps_lat",                 "REAL",     "GPS latitude (WGS-84)"),
    ("gps_lon",                 "REAL",     "GPS longitude (WGS-84)"),
    ("gps_altitude_m",          "REAL",     "GPS altitude above sea level (m)"),
    ("gps_heading_deg",         "REAL",     "Course over ground (0=N, 90=E)"),
    ("gps_speed_kmh",           "REAL",     "GPS-derived speed (independent of wheel sensors)"),
    ("gps_hdop",                "REAL",     "Horizontal dilution of precision — fix accuracy"),
    ("gps_satellites",          "INTEGER",  "Number of satellites in fix"),
    ("gps_fix_quality",         "TEXT",     "'none'|'2D'|'3D'|'DGPS'"),

    # ── B. IMU — 3-axis accelerometer + gyro (blackbox) ────────────────────
    ("accel_x_g",               "REAL",     "Longitudinal accel (+ forward, − braking) in g"),
    ("accel_y_g",               "REAL",     "Lateral accel (+ right turn) in g"),
    ("accel_z_g",               "REAL",     "Vertical accel (1.0 ≈ stationary) in g"),
    ("accel_total_g",           "REAL",     "Vector magnitude √(x²+y²+z²) in g"),
    ("gyro_roll_deg_s",         "REAL",     "Roll rate around longitudinal axis (°/s)"),
    ("gyro_pitch_deg_s",        "REAL",     "Pitch rate around lateral axis (°/s)"),
    ("gyro_yaw_deg_s",          "REAL",     "Yaw rate around vertical axis (°/s)"),
    ("tilt_angle_deg",          "REAL",     "Static tilt — used for rollover detection"),

    # ── C. Crash / Harsh-event detection (blackbox event engine) ───────────
    ("blackbox_event_type",     "TEXT",     "'normal'|'hard_brake'|'hard_accel'|'hard_cornering'|"
                                            "'swerve'|'collision_minor'|'collision_major'|'rollover'"),
    ("last_event_timestamp",    "DATETIME", "When the last non-normal event fired"),
    ("event_max_g",             "REAL",     "Peak accel during the last event (g)"),
    ("impact_severity",         "TEXT",     "'none'|'low'|'medium'|'high'|'critical'"),
    ("abs_active",              "INTEGER",  "0/1 — ABS currently engaged"),
    ("esc_active",              "INTEGER",  "0/1 — Electronic Stability Control intervening"),

    # ── D. Engine / Powertrain (OBD-II Mode 01 standard PIDs) ──────────────
    ("engine_rpm",              "REAL",     "PID 0x0C — engine speed (rpm)"),
    ("engine_load_pct",         "REAL",     "PID 0x04 — calculated load value"),
    ("engine_runtime_s",        "INTEGER",  "PID 0x1F — runtime since engine start"),
    ("coolant_temp_c",          "REAL",     "PID 0x05 — coolant temperature (°C)"),
    ("intake_air_temp_c",       "REAL",     "PID 0x0F — intake air temperature (°C)"),
    ("maf_g_per_s",             "REAL",     "PID 0x10 — mass air flow rate"),
    ("map_kpa",                 "REAL",     "PID 0x0B — manifold absolute pressure"),
    ("throttle_position_pct",   "REAL",     "PID 0x11 — absolute throttle position"),
    ("ignition_timing_adv_deg", "REAL",     "PID 0x0E — timing advance for cyl. #1"),

    # ── E. Fuel system (OBD-II) ────────────────────────────────────────────
    ("fuel_level_pct",          "REAL",     "PID 0x2F — fuel tank level input"),
    ("fuel_pressure_kpa",       "REAL",     "PID 0x0A — fuel pressure (gauge)"),
    ("fuel_rail_pressure_kpa",  "REAL",     "PID 0x22 — fuel rail pressure (relative)"),
    ("short_term_fuel_trim_pct","REAL",     "PID 0x06 — Bank 1 short-term fuel trim"),
    ("long_term_fuel_trim_pct", "REAL",     "PID 0x07 — Bank 1 long-term fuel trim"),
    ("commanded_afr",           "REAL",     "Commanded air-fuel ratio"),
    ("fuel_type",               "TEXT",     "'petrol'|'diesel'|'lpg'|'cng'|'hybrid'|'electric'"),

    # ── F. Vehicle & wheel speed ───────────────────────────────────────────
    ("vehicle_speed_kmh",       "REAL",     "PID 0x0D — vehicle speed sensor"),
    ("avg_speed_kmh",           "REAL",     "Rolling average over last sync window"),
    ("max_speed_kmh",           "REAL",     "Peak speed in the current trip"),
    ("wheel_speed_fl_kmh",      "REAL",     "ABS wheel-speed sensor — front left"),
    ("wheel_speed_fr_kmh",      "REAL",     "ABS wheel-speed sensor — front right"),
    ("wheel_speed_rl_kmh",      "REAL",     "ABS wheel-speed sensor — rear left"),
    ("wheel_speed_rr_kmh",      "REAL",     "ABS wheel-speed sensor — rear right"),

    # ── G. Emissions / aftertreatment (OBD-II) ─────────────────────────────
    ("o2_voltage_b1s1",         "REAL",     "PID 0x14 — O₂ sensor B1S1 (upstream)"),
    ("o2_voltage_b1s2",         "REAL",     "PID 0x15 — O₂ sensor B1S2 (downstream)"),
    ("catalyst_temp_b1s1_c",    "REAL",     "PID 0x3C — catalyst temp"),
    ("egr_commanded_pct",       "REAL",     "PID 0x2C — commanded EGR"),
    ("egr_actual_pct",          "REAL",     "PID 0x2D — actual EGR position"),
    ("evap_system_pressure_pa", "REAL",     "Evaporative emission system pressure"),
    ("nox_ppm",                 "REAL",     "NOx sensor concentration (diesel/Euro 6+)"),

    # ── H. 12-V electrical (OBD-II) ────────────────────────────────────────
    ("control_module_voltage_v","REAL",     "PID 0x42 — ECM supply voltage"),
    ("battery_voltage_v",       "REAL",     "Starter/auxiliary battery terminal voltage"),
    ("ambient_air_temp_c",      "REAL",     "PID 0x46 — outside air temp sensor"),

    # ── I. Brake system ────────────────────────────────────────────────────
    ("brake_pressure_bar",      "REAL",     "Master-cylinder hydraulic pressure"),
    ("brake_pedal_pct",         "REAL",     "Pedal travel sensor (0-100 %)"),

    # ── J. Steering ────────────────────────────────────────────────────────
    ("steering_angle_deg",      "REAL",     "Steering wheel absolute angle"),
    ("steering_rate_deg_s",     "REAL",     "Steering rate of change — basis for 'swerve' detection"),

    # ── K. Transmission ────────────────────────────────────────────────────
    ("transmission_fluid_temp_c", "REAL",   "ATF temperature"),
    ("gear_position",             "TEXT",   "'P'|'R'|'N'|'D'|'S'|'M'|'1'..'8'"),
    ("transmission_input_rpm",    "REAL",   "Input shaft speed"),
    ("transmission_output_rpm",   "REAL",   "Output shaft speed"),

    # ── L. TPMS — Tire Pressure Monitoring (per wheel) ─────────────────────
    ("tpms_fl_bar",             "REAL",     "Front-left tyre pressure"),
    ("tpms_fr_bar",             "REAL",     "Front-right tyre pressure"),
    ("tpms_rl_bar",             "REAL",     "Rear-left tyre pressure"),
    ("tpms_rr_bar",             "REAL",     "Rear-right tyre pressure"),
    ("tpms_fl_temp_c",          "REAL",     "Front-left tyre temperature"),
    ("tpms_fr_temp_c",          "REAL",     "Front-right tyre temperature"),
    ("tpms_rl_temp_c",          "REAL",     "Rear-left tyre temperature"),
    ("tpms_rr_temp_c",          "REAL",     "Rear-right tyre temperature"),

    # ── M. EV / Hybrid powertrain (Mode 22 / OEM-specific PIDs) ────────────
    ("battery_soc_pct",         "REAL",     "HV pack state of charge (0-100)"),
    ("battery_soh_pct",         "REAL",     "HV pack state of health (degradation)"),
    ("battery_pack_voltage_v",  "REAL",     "HV pack terminal voltage"),
    ("battery_pack_current_a",  "REAL",     "HV pack current (+ discharge, − charge)"),
    ("battery_temp_min_c",      "REAL",     "Coldest cell-group temperature"),
    ("battery_temp_max_c",      "REAL",     "Hottest cell-group temperature"),
    ("battery_cell_v_min",      "REAL",     "Minimum single-cell voltage"),
    ("battery_cell_v_max",      "REAL",     "Maximum single-cell voltage"),
    ("battery_energy_kwh",      "REAL",     "Currently available usable energy"),
    ("motor_speed_rpm",         "REAL",     "Traction motor speed"),
    ("motor_torque_nm",         "REAL",     "Estimated motor torque"),
    ("motor_temp_c",            "REAL",     "Motor winding temperature"),
    ("inverter_temp_c",         "REAL",     "Power-electronics inverter temperature"),
    ("regen_braking_pct",       "REAL",     "% of braking energy recuperated this trip"),
    ("charge_status",           "TEXT",     "'idle'|'driving'|'parked'|'charging_ac'|'charging_dc'"),
    ("charging_power_kw",       "REAL",     "Instantaneous charging power"),
    ("estimated_range_km",      "REAL",     "Estimated remaining driving range"),

    # ── N. ADAS / Active-safety event counters ─────────────────────────────
    ("abs_activations_count",       "INTEGER", "Cumulative ABS interventions"),
    ("esc_interventions_count",     "INTEGER", "Cumulative ESC interventions"),
    ("aeb_activations_count",       "INTEGER", "Autonomous Emergency Braking events"),
    ("lane_departure_warnings_count","INTEGER","LDW events"),
    ("forward_collision_warnings_count","INTEGER","FCW events"),
    ("traction_control_interventions_count","INTEGER","TC interventions"),

    # ── O. Driver-behaviour counters (telematics-grade) ────────────────────
    ("hard_brake_count",        "INTEGER",  "Hard-braking events lifetime"),
    ("hard_accel_count",        "INTEGER",  "Hard-acceleration events lifetime"),
    ("hard_cornering_count",    "INTEGER",  "Hard-cornering events lifetime"),
    ("speeding_events_count",   "INTEGER",  "Posted-limit exceedance events"),
    ("harsh_event_count_24h",   "INTEGER",  "Total harsh events in last 24 h"),
    ("idle_time_s",             "INTEGER",  "Cumulative idle time (engine on, vehicle stopped)"),
    ("night_driving_pct",       "REAL",     "% of distance driven between 22:00-06:00"),
    ("highway_driving_pct",     "REAL",     "% of distance on motorway"),
    ("urban_driving_pct",       "REAL",     "% of distance in urban roads"),
    ("eco_score",               "INTEGER",  "Eco-driving score 0-100"),
    ("safety_score",            "INTEGER",  "Safety score 0-100 (orthogonal to driving_score)"),
    ("smoothness_score",        "INTEGER",  "Smoothness score 0-100"),

    # ── P. Diagnostic Trouble Codes (OBD-II Mode 03 / 07 / 02) ─────────────
    ("mil_active",                  "INTEGER", "Malfunction Indicator Lamp on (0/1)"),
    ("dtc_count",                   "INTEGER", "Number of stored DTCs"),
    ("dtc_codes_json",              "TEXT",    "JSON array of stored P-codes (Mode 03)"),
    ("pending_dtc_codes_json",      "TEXT",    "JSON array of pending codes (Mode 07)"),
    ("distance_with_mil_on_km",     "REAL",    "PID 0x21 — distance traveled with MIL on"),
    ("distance_since_codes_cleared_km","REAL", "PID 0x31 — distance since last clear"),
    ("freeze_frame_json",           "TEXT",    "JSON snapshot of conditions when DTC stored"),

    # ── Q. Trip & odometer (in addition to existing current_odometer_km) ───
    ("trip_distance_km",        "REAL",     "Distance since last engine start"),
    ("trip_duration_s",         "INTEGER",  "Seconds since last engine start"),
    ("total_trips",             "INTEGER",  "Cumulative trip count"),
    ("total_distance_km",       "REAL",     "Lifetime distance (mirrors current_odometer_km)"),
    ("ignition_state",          "TEXT",     "'off'|'accessory'|'run'|'start'"),
    ("parked",                  "INTEGER",  "0/1 — currently parked"),

    # ── R. Blackbox device / connectivity (housekeeping) ───────────────────
    ("gsm_signal_dbm",          "INTEGER",  "Cellular signal strength (dBm)"),
    ("blackbox_firmware_version","TEXT",    "On-device firmware version"),
    ("blackbox_device_id",      "TEXT",     "Unique blackbox serial (vendor-supplied)"),
    ("blackbox_battery_pct",    "REAL",     "On-device backup battery %"),
]


def _existing_columns(cursor) -> set[str]:
    return {row[1] for row in cursor.execute("PRAGMA table_info(vehicle_telemetry)").fetchall()}


# Columns that used to live on vehicle_telemetry but are not realistically
# emitted by an OBD-II port + insurance blackbox combination. They get
# DROP-ped from the live schema on every boot so the source of truth stays
# clean. (Requires SQLite ≥ 3.35; silently skipped on older runtimes.)
_DEPRECATED_COLUMNS: list[str] = [
    "brake_temp_c",          # rotor temp sensor — track-only, not on production cars
    "alternator_current_a",  # rarely a standard PID; not exposed by typical blackboxes
    "airbag_deployed",       # SRS ECU diagnostic mode, not real-time OBD-II
]


def migrate():
    """Add every category column to vehicle_telemetry + drop deprecated ones.

    Safe on every boot — ADD COLUMN swallows 'duplicate' errors, DROP COLUMN
    is wrapped in try/except so older SQLite builds just no-op.
    """
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()

    have = _existing_columns(cursor)
    added: list[str] = []

    for col, ctype, _comment in _TELEMETRY_COLUMNS:
        if col in have:
            continue
        try:
            cursor.execute(f"ALTER TABLE vehicle_telemetry ADD COLUMN {col} {ctype}")
            added.append(col)
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                raise

    # Drop columns that no longer belong (OBD-II / blackbox feasibility cleanup).
    dropped: list[str] = []
    for col in _DEPRECATED_COLUMNS:
        if col not in have:
            continue
        try:
            cursor.execute(f"ALTER TABLE vehicle_telemetry DROP COLUMN {col}")
            dropped.append(col)
        except sqlite3.OperationalError:
            pass  # Older SQLite, or column already gone — leave the NULL ghost.

    conn.commit()
    conn.close()

    if added:
        print(f"📡 telemetry_seeder: added {len(added)} columns to vehicle_telemetry "
              f"({len(_TELEMETRY_COLUMNS)} catalogued, "
              f"{len(_TELEMETRY_COLUMNS) - len(added)} already present).")
    if dropped:
        print(f"🧹 telemetry_seeder: dropped {len(dropped)} non-OBD/blackbox columns: "
              f"{', '.join(dropped)}.")


def category_index() -> dict[str, list[str]]:
    """Inspection helper — return the catalogue grouped by section letter.

    Useful for future generators / API responses that want to expose the
    telemetry surface by source (e.g. 'gps', 'imu', 'obd_engine', etc.)
    without re-parsing the migrations list.
    """
    return {
        "gps":              [c for c, *_ in _TELEMETRY_COLUMNS if c.startswith("gps_")],
        "imu":              [c for c, *_ in _TELEMETRY_COLUMNS if c.startswith(("accel_", "gyro_", "tilt_"))],
        "crash_event":      ["blackbox_event_type", "last_event_timestamp", "event_max_g",
                             "impact_severity", "abs_active", "esc_active"],
        "obd_engine":       ["engine_rpm", "engine_load_pct", "engine_runtime_s",
                             "coolant_temp_c", "intake_air_temp_c", "maf_g_per_s",
                             "map_kpa", "throttle_position_pct", "ignition_timing_adv_deg"],
        "obd_fuel":         [c for c, *_ in _TELEMETRY_COLUMNS if c.startswith(("fuel_", "short_term", "long_term", "commanded_afr"))],
        "speed":            ["vehicle_speed_kmh", "avg_speed_kmh", "max_speed_kmh",
                             "wheel_speed_fl_kmh", "wheel_speed_fr_kmh",
                             "wheel_speed_rl_kmh", "wheel_speed_rr_kmh"],
        "emissions":        ["o2_voltage_b1s1", "o2_voltage_b1s2", "catalyst_temp_b1s1_c",
                             "egr_commanded_pct", "egr_actual_pct", "evap_system_pressure_pa", "nox_ppm"],
        "electrical_12v":   ["control_module_voltage_v", "battery_voltage_v",
                             "ambient_air_temp_c"],
        "brake":            ["brake_pressure_bar", "brake_pedal_pct"],
        "steering":         ["steering_angle_deg", "steering_rate_deg_s"],
        "transmission":     ["transmission_fluid_temp_c", "gear_position",
                             "transmission_input_rpm", "transmission_output_rpm"],
        "tpms":             [c for c, *_ in _TELEMETRY_COLUMNS if c.startswith("tpms_")],
        "ev_hybrid":        [c for c, *_ in _TELEMETRY_COLUMNS if c.startswith(("battery_", "motor_", "inverter_", "regen_", "charge_", "charging_", "estimated_range_"))],
        "adas":             [c for c, *_ in _TELEMETRY_COLUMNS if c.endswith("_count") and any(p in c for p in ("abs_activations", "esc_interventions", "aeb_", "lane_departure", "forward_collision", "traction_control"))],
        "behavior":         ["hard_brake_count", "hard_accel_count", "hard_cornering_count",
                             "speeding_events_count", "harsh_event_count_24h", "idle_time_s",
                             "night_driving_pct", "highway_driving_pct", "urban_driving_pct",
                             "eco_score", "safety_score", "smoothness_score"],
        "dtc":              ["mil_active", "dtc_count", "dtc_codes_json",
                             "pending_dtc_codes_json", "distance_with_mil_on_km",
                             "distance_since_codes_cleared_km", "freeze_frame_json"],
        "trip":             ["trip_distance_km", "trip_duration_s", "total_trips",
                             "total_distance_km", "ignition_state", "parked"],
        "device":           ["gsm_signal_dbm", "blackbox_firmware_version",
                             "blackbox_device_id", "blackbox_battery_pct"],
    }


if __name__ == "__main__":
    migrate()
    print(f"\nCategories registered: {len(category_index())}")
    for cat, cols in category_index().items():
        print(f"  {cat:<16} ({len(cols):>3} cols)")
