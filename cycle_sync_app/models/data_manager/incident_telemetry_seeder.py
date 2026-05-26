"""
Per-incident telemetry-samples seeder.

For each of the 5 demo investigations we store a 10-minute window of
blackbox + OBD-II samples at 5-second resolution (121 samples per case,
-300s to +300s relative to the impact). These rows are what the Adjuster's
Telemetry tab plays back and what the AI fraud-analysis prompt reads as
"the locked evidence record".

Idempotent: INSERT OR REPLACE on (case_number, sample_seq).
"""
import math
import random
import sqlite3
from datetime import datetime, timedelta

from .database_manager import DatabaseManager


_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS incident_telemetry_samples (
    case_number          TEXT NOT NULL,
    sample_seq           INTEGER NOT NULL,
    seconds_relative     INTEGER NOT NULL,      -- −300 (pre) … +300 (post) by 5s
    sample_time          DATETIME NOT NULL,     -- absolute timestamp

    -- Motion / dynamics
    vehicle_speed_kmh    REAL,
    engine_rpm           REAL,
    throttle_position_pct REAL,
    brake_pressure_bar   REAL,
    brake_pedal_pct      REAL,
    steering_angle_deg   REAL,
    steering_rate_deg_s  REAL,

    -- IMU
    accel_x_g            REAL,
    accel_y_g            REAL,
    accel_z_g            REAL,
    accel_total_g        REAL,
    gyro_roll_deg_s      REAL,
    gyro_pitch_deg_s     REAL,
    gyro_yaw_deg_s       REAL,

    -- GPS
    gps_lat              REAL,
    gps_lon              REAL,
    gps_speed_kmh        REAL,

    -- Tyres
    tpms_fl_bar          REAL,
    tpms_fr_bar          REAL,
    tpms_rl_bar          REAL,
    tpms_rr_bar          REAL,

    -- Critical states
    abs_active           INTEGER,
    esc_active           INTEGER,
    airbag_deployed      INTEGER,

    -- Powertrain
    coolant_temp_c       REAL,
    fuel_level_pct       REAL,
    battery_soc_pct      REAL,

    -- Event annotation
    event_flag           TEXT,                  -- 'normal' | 'fcw' | 'abs_engaged' | 'IMPACT' | 'airbag' | …

    PRIMARY KEY (case_number, sample_seq)
)
"""

_INDEX_DDL = (
    "CREATE INDEX IF NOT EXISTS idx_samples_case_t "
    "ON incident_telemetry_samples(case_number, seconds_relative)"
)

# Each profile gives the impact's absolute time-of-day so timestamps look right.
# (Date comes from investigations.incident_date.)
_IMPACT_TIME = {
    "CASE-2024-00142": "11:47:00",
    "CASE-2024-00287": "08:23:00",
    "CASE-2024-00391": "16:51:00",
    "CASE-2025-00012": "14:12:00",
    "CASE-2025-00045": "21:38:00",
}

# Powertrain → which engine vs. battery fields make sense.
_POWERTRAIN = {
    "CASE-2024-00142": "BEV",     # Maserati Grecale Folgore
    "CASE-2024-00287": "BEV",     # Tesla Model 3
    "CASE-2024-00391": "BEV",     # Fiat 500e
    "CASE-2025-00012": "ICE",     # VW Golf
    "CASE-2025-00045": "ICE",     # BMW X5
}


# ──────────────────────────────────────────────────────────────────────────
# Piecewise linear interpolation between (t, value) keyframes.
# ──────────────────────────────────────────────────────────────────────────
def _interp(t, frames):
    if t <= frames[0][0]:
        return frames[0][1]
    if t >= frames[-1][0]:
        return frames[-1][1]
    for i in range(1, len(frames)):
        t1, v1 = frames[i]
        if t < t1:
            t0, v0 = frames[i - 1]
            if t1 == t0:
                return v1
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return frames[-1][1]


def _step(t, frames):
    """Like _interp but holds each value until the next keyframe (no blend)."""
    if t < frames[0][0]:
        return frames[0][1]
    last = frames[0][1]
    for kt, kv in frames:
        if t < kt:
            return last
        last = kv
    return last


def _event_flag(t, frames):
    return _step(t, frames)


# ──────────────────────────────────────────────────────────────────────────
# CASE-2024-00142 — Maserati Grecale Folgore, red-light runner, 4.2 g
# ──────────────────────────────────────────────────────────────────────────
# Antonio Moretti's BEV approaches Via Appia Nuova × Via di Cinecittà.
# Light goes yellow → red over T-20 to T-15. He does NOT brake.
# Crosses red at 55 km/h. T-1.2s ABS engages (collapsed into sample t=0 at 5s grain).
# T=0: front collision at 4.2 g long, 1.1 g lateral. Front + passenger airbags.
def _profile_142(t):
    SPEED = _interp(t, [(-300, 38), (-240, 46), (-150, 52), (-60, 55), (-15, 55),
                        (-5, 55), (0, 8), (5, 0), (300, 0)])
    THROT = _interp(t, [(-300, 14), (-150, 18), (-30, 22), (-15, 21), (-5, 19),
                        (0, 0), (300, 0)])
    BRK_P = _interp(t, [(-300, 0.5), (-5, 0.5), (0, 95), (5, 18), (10, 0.5), (300, 0.5)])
    BRK_D = _interp(t, [(-300, 0), (-5, 0), (0, 100), (5, 30), (10, 0), (300, 0)])
    AX    = _interp(t, [(-300, 0.04), (-5, 0.02), (0, -4.2), (5, -0.4), (10, 0), (300, 0)])
    AY    = _interp(t, [(-300, 0.02), (-5, 0.0), (0, -1.1), (5, 0.0), (300, 0)])
    AZ    = _interp(t, [(-300, 0.98), (-5, 0.98), (0, 0.85), (5, 1.02), (300, 1.0)])
    YAW   = _interp(t, [(-300, 0.5), (-5, 0.4), (0, 22.0), (5, 4.0), (10, 0.5), (300, 0)])
    STR   = _interp(t, [(-300, 1.2), (-30, 2.0), (-5, 1.8), (0, 12.0), (5, 0), (300, 0)])
    # GPS approaching from the south along Via Appia Nuova
    LAT   = _interp(t, [(-300, 41.8487), (-60, 41.8520), (-15, 41.8528), (0, 41.8530),
                        (5, 41.8530), (300, 41.8530)])
    LON   = _interp(t, [(-300, 12.5396), (-60, 12.5407), (-15, 12.5409), (0, 12.5410),
                        (5, 12.5410), (300, 12.5410)])
    FLAG  = _event_flag(t, [
        (-300, "normal"),
        (-30,  "approach_intersection"),
        (-20,  "light_yellow"),
        (-15,  "light_red"),
        (-5,   "ldw_alert"),
        (0,    "IMPACT"),
        (5,    "airbag_deployed"),
        (15,   "vehicle_stopped"),
        (60,   "ignition_off"),
    ])
    return {
        "vehicle_speed_kmh": SPEED, "gps_speed_kmh": SPEED,
        "engine_rpm": None,  # BEV
        "throttle_position_pct": THROT,
        "brake_pressure_bar": BRK_P, "brake_pedal_pct": BRK_D,
        "steering_angle_deg": STR, "steering_rate_deg_s": 0.5 if abs(t) > 10 else 8.0,
        "accel_x_g": AX, "accel_y_g": AY, "accel_z_g": AZ,
        "accel_total_g": math.sqrt(AX*AX + AY*AY + AZ*AZ),
        "gyro_roll_deg_s": 0.4, "gyro_pitch_deg_s": 0.3 if t < 0 else 2.0,
        "gyro_yaw_deg_s": YAW,
        "gps_lat": LAT, "gps_lon": LON,
        "tpms_fl_bar": 2.32, "tpms_fr_bar": 2.30, "tpms_rl_bar": 2.34, "tpms_rr_bar": 2.31,
        "abs_active": 1 if -2 <= t <= 1 else 0,
        "esc_active": 1 if 0 <= t <= 5 else 0,
        "airbag_deployed": 1 if t >= 0 else 0,
        "coolant_temp_c": None,  # BEV
        "fuel_level_pct": None,
        "battery_soc_pct": _interp(t, [(-300, 68.5), (0, 67.1), (300, 67.1)]),
        "event_flag": FLAG,
    }


# ──────────────────────────────────────────────────────────────────────────
# CASE-2024-00287 — Tesla Model 3, low-speed rear-end on Tangenziale, 1.8 g
# ──────────────────────────────────────────────────────────────────────────
# Maria Russo is sitting still in stop-and-go highway traffic. DHL van
# strikes her from behind at ~25 km/h relative. Accel_x is POSITIVE
# (forces vehicle forward). No airbag, no injuries, ESC active to stabilise.
def _profile_287(t):
    # Heavy congestion — speed oscillates 0–18 km/h until impact moment.
    if t < -10:
        SPEED = max(0, 10 + 8 * math.sin(t / 12))
    elif t < 0:
        SPEED = 0   # stationary in queue
    elif t < 5:
        SPEED = 6   # shoved forward 1-2 m
    else:
        SPEED = 0
    THROT = max(0, 10 + 8 * math.sin(t / 12)) if t < -10 else 0
    BRK_D = 60 if -10 <= t < 0 else (0 if t > 5 else 25)
    BRK_P = 12 if -10 <= t < 0 else (0.5 if t > 5 else 3)
    AX    = _interp(t, [(-300, 0.0), (-5, 0.0), (0, 1.8), (5, 0.2), (15, 0), (300, 0)])
    AY    = _interp(t, [(-300, 0.0), (0, 0.4), (5, 0.0), (300, 0)])
    AZ    = _interp(t, [(-300, 0.98), (0, 1.05), (300, 0.98)])
    LAT   = 45.4980
    LON   = _interp(t, [(-300, 9.2690), (-60, 9.2705), (0, 9.2710), (300, 9.2710)])
    FLAG  = _event_flag(t, [
        (-300, "normal_congestion"),
        (-30,  "stopped_in_traffic"),
        (0,    "IMPACT"),
        (5,    "vehicle_shoved"),
        (15,   "esc_stabilizing"),
        (60,   "stationary"),
    ])
    return {
        "vehicle_speed_kmh": SPEED, "gps_speed_kmh": SPEED,
        "engine_rpm": None,  # BEV
        "throttle_position_pct": THROT,
        "brake_pressure_bar": BRK_P, "brake_pedal_pct": BRK_D,
        "steering_angle_deg": 1.0, "steering_rate_deg_s": 0.2,
        "accel_x_g": AX, "accel_y_g": AY, "accel_z_g": AZ,
        "accel_total_g": math.sqrt(AX*AX + AY*AY + AZ*AZ),
        "gyro_roll_deg_s": 0.2, "gyro_pitch_deg_s": 1.5 if t == 0 else 0.3,
        "gyro_yaw_deg_s": 0.3,
        "gps_lat": LAT, "gps_lon": LON,
        "tpms_fl_bar": 2.31, "tpms_fr_bar": 2.30, "tpms_rl_bar": 2.32, "tpms_rr_bar": 2.30,
        "abs_active": 0,
        "esc_active": 1 if 0 <= t <= 20 else 0,
        "airbag_deployed": 0,
        "coolant_temp_c": None, "fuel_level_pct": None,
        "battery_soc_pct": _interp(t, [(-300, 72.0), (300, 71.9)]),
        "event_flag": FLAG,
    }


# ──────────────────────────────────────────────────────────────────────────
# CASE-2024-00391 — Fiat 500e, severe rear-end of farm tractor, 6.1 g
# ──────────────────────────────────────────────────────────────────────────
# Nicola Caruso cruises at 78 km/h on SP27. Slow tractor ahead. FCW fires
# at T-2s; brake applied 0.8s late at T-1.2s. Pads at 96% wear — ABS
# fights to modulate. Multiple airbags deploy. Highest 2024 g-event.
def _profile_391(t):
    SPEED = _interp(t, [(-300, 72), (-60, 78), (-10, 78), (-5, 76), (-2, 70),
                        (0, 0), (5, 0), (300, 0)])
    THROT = _interp(t, [(-300, 28), (-30, 32), (-10, 30), (-5, 25), (-2, 5),
                        (0, 0), (300, 0)])
    BRK_P = _interp(t, [(-300, 0.5), (-5, 0.5), (-2, 45), (-1, 95),
                        (0, 110), (5, 25), (10, 0.5), (300, 0.5)])
    BRK_D = _interp(t, [(-300, 0), (-2, 30), (-1, 95), (0, 100), (5, 35), (10, 0), (300, 0)])
    AX    = _interp(t, [(-300, 0.05), (-5, 0.02), (-2, -0.4), (-1, -1.2),
                        (0, -6.1), (5, -0.3), (15, 0), (300, 0)])
    AY    = _interp(t, [(-300, 0.02), (0, -0.4), (5, 0), (300, 0)])
    AZ    = _interp(t, [(-300, 0.98), (-5, 0.98), (0, 0.7), (5, 1.05), (300, 1.0)])
    LAT   = _interp(t, [(-300, 45.7180), (-60, 45.7210), (0, 45.7220), (5, 45.7220), (300, 45.7220)])
    LON   = _interp(t, [(-300, 7.2620), (-60, 7.2670), (0, 7.2680), (5, 7.2680), (300, 7.2680)])
    FLAG  = _event_flag(t, [
        (-300, "normal_cruise"),
        (-30,  "tractor_in_view"),
        (-15,  "closing_in"),
        (-2,   "FCW_FORWARD_COLLISION_WARNING"),
        (-1,   "brake_applied_late"),
        (0,    "IMPACT"),
        (5,    "multi_airbag_deployed"),
        (30,   "vehicle_stopped"),
        (60,   "ignition_off"),
    ])
    return {
        "vehicle_speed_kmh": SPEED, "gps_speed_kmh": SPEED,
        "engine_rpm": None,
        "throttle_position_pct": THROT,
        "brake_pressure_bar": BRK_P, "brake_pedal_pct": BRK_D,
        "steering_angle_deg": 2.5, "steering_rate_deg_s": 0.6 if t > -2 else 0.4,
        "accel_x_g": AX, "accel_y_g": AY, "accel_z_g": AZ,
        "accel_total_g": math.sqrt(AX*AX + AY*AY + AZ*AZ),
        "gyro_roll_deg_s": 0.3, "gyro_pitch_deg_s": 0.4 if t < 0 else 4.0,
        "gyro_yaw_deg_s": 0.6 if t != 0 else 8.0,
        "gps_lat": LAT, "gps_lon": LON,
        "tpms_fl_bar": 2.34, "tpms_fr_bar": 2.32, "tpms_rl_bar": 2.36, "tpms_rr_bar": 2.33,
        "abs_active": 1 if -2 <= t <= 1 else 0,
        "esc_active": 1 if 0 <= t <= 8 else 0,
        "airbag_deployed": 1 if t >= 0 else 0,
        "coolant_temp_c": None, "fuel_level_pct": None,
        "battery_soc_pct": _interp(t, [(-300, 51.0), (0, 49.2), (300, 49.2)]),
        "event_flag": FLAG,
    }


# ──────────────────────────────────────────────────────────────────────────
# CASE-2025-00012 — VW Golf, T-junction side impact (resolved)
# ──────────────────────────────────────────────────────────────────────────
# Aurora Martini, ICE Golf, urban Rome. Right-of-way at the junction.
# Peugeot 208 fails to yield from the left at T=0, strikes the driver-
# side B-pillar at 35 km/h. 3.0 g LATERAL. Side curtain (driver) deploys.
def _profile_012(t):
    SPEED = _interp(t, [(-300, 30), (-60, 35), (-15, 32), (-5, 30), (0, 15),
                        (5, 8), (10, 0), (300, 0)])
    RPM   = _interp(t, [(-300, 2100), (-30, 2300), (-5, 2000), (0, 1800),
                        (5, 1000), (10, 800), (300, 0)])
    THROT = _interp(t, [(-300, 18), (-30, 22), (-5, 15), (0, 0), (300, 0)])
    BRK_P = _interp(t, [(-300, 0.5), (-1, 0.5), (0, 35), (5, 75), (10, 25), (15, 0.5), (300, 0.5)])
    BRK_D = _interp(t, [(-300, 0), (0, 40), (5, 80), (10, 30), (15, 0), (300, 0)])
    AX    = _interp(t, [(-300, 0.03), (0, -0.5), (5, -1.4), (10, -0.2), (300, 0)])
    AY    = _interp(t, [(-300, 0.02), (-5, 0.0), (0, -3.0), (5, -0.8), (10, 0), (300, 0)])
    AZ    = _interp(t, [(-300, 0.98), (0, 0.95), (300, 1.0)])
    YAW   = _interp(t, [(-300, 0.4), (0, 38.0), (3, 18.0), (8, 4.0), (15, 0.5), (300, 0)])
    LAT   = _interp(t, [(-300, 41.8458), (-30, 41.8476), (0, 41.8480), (5, 41.8481), (10, 41.8482), (300, 41.8482)])
    LON   = _interp(t, [(-300, 12.5772), (-30, 12.5766), (0, 12.5765), (300, 12.5765)])
    FLAG  = _event_flag(t, [
        (-300, "normal_cruise"),
        (-30,  "approach_junction"),
        (-5,   "right_of_way"),
        (0,    "IMPACT_SIDE"),
        (5,    "esc_intervention"),
        (10,   "vehicle_stopped"),
        (30,   "post_crash_stationary"),
    ])
    return {
        "vehicle_speed_kmh": SPEED, "gps_speed_kmh": SPEED,
        "engine_rpm": RPM,
        "throttle_position_pct": THROT,
        "brake_pressure_bar": BRK_P, "brake_pedal_pct": BRK_D,
        "steering_angle_deg": 0.5 if t < 0 else (28 if t == 5 else 4),
        "steering_rate_deg_s": 1.0 if abs(t) > 5 else 22.0,
        "accel_x_g": AX, "accel_y_g": AY, "accel_z_g": AZ,
        "accel_total_g": math.sqrt(AX*AX + AY*AY + AZ*AZ),
        "gyro_roll_deg_s": 0.5 if t != 0 else 6.0,
        "gyro_pitch_deg_s": 0.4,
        "gyro_yaw_deg_s": YAW,
        "gps_lat": LAT, "gps_lon": LON,
        "tpms_fl_bar": 2.30, "tpms_fr_bar": 2.31, "tpms_rl_bar": 2.30, "tpms_rr_bar": 2.32,
        "abs_active": 1 if 0 <= t <= 5 else 0,
        "esc_active": 1 if 0 <= t <= 10 else 0,
        "airbag_deployed": 1 if t >= 0 else 0,  # side curtain L deployed at impact
        "coolant_temp_c": _interp(t, [(-300, 92), (0, 94), (60, 88), (300, 78)]),
        "fuel_level_pct": _interp(t, [(-300, 62.0), (300, 61.8)]),
        "battery_soc_pct": None,
        "event_flag": FLAG,
    }


# ──────────────────────────────────────────────────────────────────────────
# CASE-2025-00045 — BMW X5, head-on collision on wet provincial road, 5.5 g
# ──────────────────────────────────────────────────────────────────────────
# Monica Rinaldi, ICE BMW X5, night driving on wet SP35. Oncoming Renault
# Captur (driver asleep) crosses center line at T=-0.4s. Combined closing
# speed ~110 km/h. ABS engages 0.4s before impact (collapsed into t=0 sample).
# Both front + knee airbags deploy. 5.5 g longitudinal.
def _profile_045(t):
    SPEED = _interp(t, [(-300, 58), (-60, 65), (-10, 65), (-1, 62), (0, 0),
                        (5, 0), (300, 0)])
    RPM   = _interp(t, [(-300, 2400), (-10, 2600), (-1, 2200), (0, 0), (300, 0)])
    THROT = _interp(t, [(-300, 22), (-10, 24), (-1, 0), (0, 0), (300, 0)])
    BRK_P = _interp(t, [(-300, 0.5), (-1, 95), (0, 110), (5, 20), (10, 0.5), (300, 0.5)])
    BRK_D = _interp(t, [(-300, 0), (-1, 100), (0, 100), (5, 30), (10, 0), (300, 0)])
    AX    = _interp(t, [(-300, 0.05), (-5, 0.02), (-1, -1.6), (0, -5.5),
                        (5, -0.3), (15, 0), (300, 0)])
    AY    = _interp(t, [(-300, 0.02), (-1, -0.4), (0, -0.8), (5, 0.0), (300, 0)])
    AZ    = _interp(t, [(-300, 0.98), (-1, 0.95), (0, 0.65), (5, 1.05), (300, 1.0)])
    LAT   = _interp(t, [(-300, 45.6520), (-60, 45.6490), (-10, 45.6482), (0, 45.6480),
                        (5, 45.6480), (300, 45.6480)])
    LON   = _interp(t, [(-300, 9.0210), (-60, 9.0203), (-10, 9.0201), (0, 9.0200),
                        (5, 9.0200), (300, 9.0200)])
    FLAG  = _event_flag(t, [
        (-300, "normal_cruise_wet_road"),
        (-30,  "oncoming_traffic"),
        (-2,   "oncoming_drifted_left"),
        (-1,   "abs_engaged_emergency"),
        (0,    "IMPACT_HEAD_ON"),
        (5,    "airbag_deployed_all"),
        (30,   "vehicle_stopped"),
        (60,   "ignition_off"),
    ])
    return {
        "vehicle_speed_kmh": SPEED, "gps_speed_kmh": SPEED,
        "engine_rpm": RPM,
        "throttle_position_pct": THROT,
        "brake_pressure_bar": BRK_P, "brake_pedal_pct": BRK_D,
        "steering_angle_deg": _interp(t, [(-300, 1.5), (-1, 16), (0, 8), (5, 0), (300, 0)]),
        "steering_rate_deg_s": 1.0 if abs(t) > 5 else 14.0,
        "accel_x_g": AX, "accel_y_g": AY, "accel_z_g": AZ,
        "accel_total_g": math.sqrt(AX*AX + AY*AY + AZ*AZ),
        "gyro_roll_deg_s": 0.4 if t != 0 else 5.0,
        "gyro_pitch_deg_s": 0.5 if t != 0 else 6.5,
        "gyro_yaw_deg_s": 0.6 if t != 0 else 4.5,
        "gps_lat": LAT, "gps_lon": LON,
        "tpms_fl_bar": 2.30, "tpms_fr_bar": 2.31, "tpms_rl_bar": 2.29, "tpms_rr_bar": 2.30,
        "abs_active": 1 if -1 <= t <= 1 else 0,
        "esc_active": 1 if 0 <= t <= 6 else 0,
        "airbag_deployed": 1 if t >= 0 else 0,
        "coolant_temp_c": _interp(t, [(-300, 89), (-30, 91), (0, 96), (60, 78), (300, 28)]),
        "fuel_level_pct": _interp(t, [(-300, 47.2), (300, 47.0)]),
        "battery_soc_pct": None,
        "event_flag": FLAG,
    }


_PROFILES = {
    "CASE-2024-00142": _profile_142,
    "CASE-2024-00287": _profile_287,
    "CASE-2024-00391": _profile_391,
    "CASE-2025-00012": _profile_012,
    "CASE-2025-00045": _profile_045,
}


# ──────────────────────────────────────────────────────────────────────────
# Insertion / bootstrap
# ──────────────────────────────────────────────────────────────────────────
_INSERT_SQL = """
INSERT OR REPLACE INTO incident_telemetry_samples (
    case_number, sample_seq, seconds_relative, sample_time,
    vehicle_speed_kmh, engine_rpm, throttle_position_pct,
    brake_pressure_bar, brake_pedal_pct,
    steering_angle_deg, steering_rate_deg_s,
    accel_x_g, accel_y_g, accel_z_g, accel_total_g,
    gyro_roll_deg_s, gyro_pitch_deg_s, gyro_yaw_deg_s,
    gps_lat, gps_lon, gps_speed_kmh,
    tpms_fl_bar, tpms_fr_bar, tpms_rl_bar, tpms_rr_bar,
    abs_active, esc_active, airbag_deployed,
    coolant_temp_c, fuel_level_pct, battery_soc_pct,
    event_flag
) VALUES (?,?,?,?, ?,?,?, ?,?, ?,?, ?,?,?,?, ?,?,?, ?,?,?, ?,?,?,?, ?,?,?, ?,?,?, ?)
"""


def _impact_datetime(cursor, case_no):
    row = cursor.execute(
        "SELECT incident_date FROM investigations WHERE case_number=?",
        (case_no,),
    ).fetchone()
    if not row or not row[0]:
        return datetime.now()
    incident_date = str(row[0])[:10]   # 'YYYY-MM-DD'
    t = _IMPACT_TIME.get(case_no, "12:00:00")
    try:
        return datetime.strptime(f"{incident_date}T{t}", "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return datetime.now()


def _seed_samples_for_case(cursor, case_no, profile_fn):
    impact_dt = _impact_datetime(cursor, case_no)
    seq = 0
    for t in range(-300, 301, 5):
        s = profile_fn(t)
        sample_time = impact_dt + timedelta(seconds=t)
        cursor.execute(_INSERT_SQL, (
            case_no, seq, t, sample_time.isoformat(timespec="seconds"),
            s.get("vehicle_speed_kmh"), s.get("engine_rpm"), s.get("throttle_position_pct"),
            s.get("brake_pressure_bar"), s.get("brake_pedal_pct"),
            s.get("steering_angle_deg"), s.get("steering_rate_deg_s"),
            s.get("accel_x_g"), s.get("accel_y_g"), s.get("accel_z_g"), s.get("accel_total_g"),
            s.get("gyro_roll_deg_s"), s.get("gyro_pitch_deg_s"), s.get("gyro_yaw_deg_s"),
            s.get("gps_lat"), s.get("gps_lon"), s.get("gps_speed_kmh"),
            s.get("tpms_fl_bar"), s.get("tpms_fr_bar"), s.get("tpms_rl_bar"), s.get("tpms_rr_bar"),
            s.get("abs_active"), s.get("esc_active"), s.get("airbag_deployed"),
            s.get("coolant_temp_c"), s.get("fuel_level_pct"), s.get("battery_soc_pct"),
            s.get("event_flag"),
        ))
        seq += 1
    return seq


def migrate_and_seed():
    """Create the table + (re)seed the 5 demo windows. Idempotent."""
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()

    cursor.execute(_TABLE_DDL)
    cursor.execute(_INDEX_DDL)
    conn.commit()

    total = 0
    for case_no, profile_fn in _PROFILES.items():
        # Only seed if the investigation actually exists.
        exists = cursor.execute(
            "SELECT 1 FROM investigations WHERE case_number=?", (case_no,)
        ).fetchone()
        if not exists:
            continue
        total += _seed_samples_for_case(cursor, case_no, profile_fn)
    conn.commit()
    conn.close()

    if total:
        print(f"⏱️  incident_telemetry_seeder: stored "
              f"{total} samples across {len(_PROFILES)} cases "
              f"(±5 min @ 5 s resolution).")


if __name__ == "__main__":
    migrate_and_seed()
