"""
Investigation seeder — adds the Adjuster-Portal columns to the partner DB and
inserts a handful of demo cases so the /api/db/investigations endpoints have
something to return.

Idempotent: safe to run repeatedly. ALTER TABLE failures (column exists) are
swallowed silently; INSERT OR IGNORE keeps the seed unique by case_number.
"""
import json
import os
import sqlite3

from .database_manager import DatabaseManager


# Columns the Adjuster portal expects on top of the partner's minimal schema.
_INVESTIGATION_MIGRATIONS = [
    "ALTER TABLE investigations ADD COLUMN incident_location TEXT",
    "ALTER TABLE investigations ADD COLUMN incident_lat REAL",
    "ALTER TABLE investigations ADD COLUMN incident_lng REAL",
    "ALTER TABLE investigations ADD COLUMN incident_description TEXT",
    "ALTER TABLE investigations ADD COLUMN speed_at_impact REAL",
    "ALTER TABLE investigations ADD COLUMN g_force_max REAL",
    "ALTER TABLE investigations ADD COLUMN g_force_lateral REAL",
    "ALTER TABLE investigations ADD COLUMN abs_triggered INTEGER",
    "ALTER TABLE investigations ADD COLUMN airbag_deployed INTEGER",
    "ALTER TABLE investigations ADD COLUMN tpms_snapshot_json TEXT",
    "ALTER TABLE investigations ADD COLUMN coolant_temp REAL",
    "ALTER TABLE investigations ADD COLUMN coolant_pressure REAL",
    "ALTER TABLE investigations ADD COLUMN ai_damage_assessment_json TEXT",
    "ALTER TABLE investigations ADD COLUMN ai_repair_estimate_eur REAL",
    "ALTER TABLE investigations ADD COLUMN ai_fraud_analysis TEXT",
    "ALTER TABLE investigations ADD COLUMN ai_verdict TEXT",
    "ALTER TABLE investigations ADD COLUMN photos_json TEXT",
    "ALTER TABLE investigations ADD COLUMN reconstruction_video TEXT",
    "ALTER TABLE investigations ADD COLUMN assigned_adjuster TEXT",
    "ALTER TABLE investigations ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE investigations ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE investigations ADD COLUMN resolved_at DATETIME",
]

_INVESTIGATION_PHOTOS_DDL = """
CREATE TABLE IF NOT EXISTS investigation_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number TEXT NOT NULL,
    filename TEXT NOT NULL,
    caption TEXT,
    photo_type TEXT DEFAULT 'damage',
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_number) REFERENCES investigations(case_number)
)
"""

_UNIQUE_CASE_INDEX_DDL = (
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_investigations_case_number "
    "ON investigations(case_number)"
)


def _pick_demo_vins(cursor) -> list[tuple]:
    """Choose one vehicle per car_model so the seed covers diverse brands."""
    rows = cursor.execute(
        """
        SELECT v.vin, v.plate_number, v.driver_name, v.region_name,
               cm.manufacturer, cm.model_name
        FROM vehicles v
        JOIN car_models cm ON v.model_id = cm.id
        WHERE v.plate_number IS NOT NULL
        GROUP BY cm.id
        ORDER BY cm.id
        LIMIT 5
        """
    ).fetchall()
    return rows


def _seed_investigations(conn) -> int:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM investigations")
    if cursor.fetchone()[0] > 0:
        return 0  # Already seeded.

    vins = _pick_demo_vins(cursor)
    if len(vins) < 1:
        print("⚠️  Cannot seed investigations: vehicles table is empty.")
        return 0

    demo_cases = [
        # (case_number, incident_date, type, status, priority, fraud, speed, g_max, g_lat,
        #  abs, airbag, location, description, ai_verdict, repair_eur)
        ("CASE-2024-00142", "2024-11-02", "collision",   "open",         "high",     72.0, 55.0, 4.2, 1.1, 1, 1,
         "Via Appia Nuova, Roma",
         "Front collision at intersection. Driver ran red light at 55 km/h. Airbags deployed.",
         None, 4800.0),
        ("CASE-2024-00287", "2024-11-15", "rear_end",    "under_review", "medium",   15.0, 25.0, 1.8, 0.4, 0, 0,
         "Tangenziale Est, Milano",
         "Low-speed rear-end collision in highway traffic. Bumper and tailgate damage.",
         None, 1800.0),
        ("CASE-2024-00391", "2024-12-22", "rear_end",    "open",         "critical", 89.0, 78.0, 6.1, 1.8, 1, 1,
         "A1 — km 488, Bologna",
         "Severe rear-end collision. Driver ignored multiple brake warnings. Brake pads critically worn.",
         None, 12400.0),
        ("CASE-2025-00012", "2025-03-10", "side_impact", "resolved",     "medium",    8.0, 35.0, 3.0, 1.4, 1, 0,
         "Piazza Maggiore, Bologna",
         "Side impact at T-junction. Third party vehicle failed to yield. Moderate door/panel damage.",
         "Claim Approved — third-party at fault.", 3200.0),
        ("CASE-2025-00045", "2025-04-18", "collision",   "under_review", "high",     42.0, 62.0, 5.5, 1.6, 1, 1,
         "SS16, Bari",
         "Head-on collision on provincial road. Other driver crossed center line. Significant front damage.",
         None, 7600.0),
    ]

    tpms_normal = json.dumps({"fl": 2.34, "fr": 1.52, "rl": 2.37, "rr": 2.38})

    seeded = 0
    for i, (vin_row, case) in enumerate(zip(vins, demo_cases)):
        vin = vin_row[0]
        (case_no, date, itype, status, prio, fraud, speed, g_max, g_lat,
         abs_t, airbag, loc, desc, verdict, repair) = case
        cursor.execute(
            """
            INSERT OR IGNORE INTO investigations (
                case_number, vehicle_vin, incident_date, incident_type,
                status, priority, fraud_risk_score, speed_at_impact,
                g_force_max, g_force_lateral, abs_triggered, airbag_deployed,
                incident_location, incident_description,
                tpms_snapshot_json, coolant_temp,
                ai_repair_estimate_eur, ai_verdict,
                assigned_adjuster
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                case_no, vin, date, itype, status, prio, fraud, speed,
                g_max, g_lat, abs_t, airbag, loc, desc,
                tpms_normal, 95.0 + (i * 1.5),
                repair, verdict, "Default Adjuster",
            ),
        )
        seeded += cursor.rowcount

    conn.commit()
    return seeded


# ────────────────────────────────────────────────────────────────────────────
# Rich per-case enrichment (overwritten on every boot — canonical demo state).
# ────────────────────────────────────────────────────────────────────────────

_ENRICHMENTS: dict[str, dict] = {
    "CASE-2024-00142": {
        "incident_location": "Via Appia Nuova × Via di Cinecittà, Roma",
        "incident_lat": 41.8530,
        "incident_lng": 12.5410,
        "incident_description": (
            "11:47 local time. Maserati Grecale Folgore entered the intersection "
            "against a red signal, striking a Fiat Panda crossing legally. ABS engaged "
            "1.2 s before impact (10.4 m skid). Front + passenger airbags deployed. "
            "Minor whiplash to Antonio Moretti; third party reported moderate. "
            "Police case INC-2024-00921. Blackbox captured 4.2 g longitudinal / 1.1 g "
            "lateral. Brake-pad wear front 82% / rear 65% — driver dismissed a "
            "VeriTwin maintenance alert 11 days prior."
        ),
        "ai_damage_assessment_json": json.dumps({
            "areas": [
                {"area": "front_bumper",           "severity": "severe",   "action": "replace"},
                {"area": "hood",                   "severity": "severe",   "action": "replace"},
                {"area": "front_radiator_support", "severity": "moderate", "action": "repair"},
                {"area": "windshield",             "severity": "moderate", "action": "replace"},
                {"area": "driver_airbag",          "severity": "deployed", "action": "replace"},
                {"area": "passenger_airbag",       "severity": "deployed", "action": "replace"},
                {"area": "front_left_headlight",   "severity": "severe",   "action": "replace"},
                {"area": "front_right_headlight",  "severity": "moderate", "action": "replace"},
            ],
            "structural_damage": True,
            "drivable": False,
        }),
        "assigned_adjuster": "Giulia Bianchi",
    },
    "CASE-2024-00287": {
        "incident_location": "Tangenziale Est Milano — km 32 northbound",
        "incident_lat": 45.4980,
        "incident_lng": 9.2710,
        "incident_description": (
            "08:23 local time, stop-and-go highway traffic. Maria Russo's Tesla Model 3 "
            "was struck from behind by a DHL delivery van while stationary. Relative "
            "impact speed ~25 km/h. ABS not engaged (already at rest). 1.8 g longitudinal, "
            "0.4 g lateral. No airbag deployment. No injuries. Third party admitted "
            "liability on-scene. Russo's VSI score 88 — clean driving history, 2,847 km "
            "this month with zero harsh-event flags."
        ),
        "ai_damage_assessment_json": json.dumps({
            "areas": [
                {"area": "rear_bumper",       "severity": "moderate", "action": "replace"},
                {"area": "tailgate",          "severity": "moderate", "action": "repair_pdr"},
                {"area": "rear_panel_left",   "severity": "minor",    "action": "paint"},
                {"area": "rear_panel_right",  "severity": "minor",    "action": "paint"},
                {"area": "rear_tail_light_l", "severity": "minor",    "action": "replace"},
            ],
            "structural_damage": False,
            "drivable": True,
        }),
        "assigned_adjuster": "Marco Greco",
    },
    "CASE-2024-00391": {
        "incident_location": "SP 27 Aosta–Sarre, km 4.2",
        "incident_lat": 45.7220,
        "incident_lng": 7.2680,
        "incident_description": (
            "16:51 local time. Nicola Caruso's Fiat 500e failed to stop behind a slow-"
            "moving farm tractor and struck it at 78 km/h. Brake pedal applied 0.8 s "
            "after the forward-collision warning (FCW); pad wear 96% on both axles — "
            "metal-on-metal contact recorded by VSI in the last 320 km. Six 'BRAKE WEAR "
            "CRITICAL' alerts dismissed via the driver app in the preceding 14 days. "
            "Front + side airbags deployed. Driver moderate injury (chest contusions, "
            "transported to Ospedale Parini). 6.1 g longitudinal — highest VeriTwin "
            "reading of 2024. Fraud risk 89: insurer position is CASKO denial on "
            "gross-negligence grounds."
        ),
        "ai_damage_assessment_json": json.dumps({
            "areas": [
                {"area": "front_bumper",         "severity": "destroyed", "action": "replace"},
                {"area": "hood",                 "severity": "severe",    "action": "replace"},
                {"area": "front_crash_box",      "severity": "severe",    "action": "replace"},
                {"area": "radiator_assembly",    "severity": "severe",    "action": "replace"},
                {"area": "ac_condenser",         "severity": "severe",    "action": "replace"},
                {"area": "windshield",           "severity": "severe",    "action": "replace"},
                {"area": "driver_airbag",        "severity": "deployed",  "action": "replace"},
                {"area": "passenger_airbag",     "severity": "deployed",  "action": "replace"},
                {"area": "side_curtain_l",       "severity": "deployed",  "action": "replace"},
                {"area": "front_subframe",       "severity": "moderate",  "action": "straighten"},
                {"area": "brake_pads_all",       "severity": "destroyed", "action": "replace"},
                {"area": "front_brake_discs",    "severity": "severe",    "action": "replace"},
            ],
            "structural_damage": True,
            "drivable": False,
        }),
        "assigned_adjuster": "Federica Conti",
    },
    "CASE-2025-00012": {
        "incident_location": "Via Tuscolana × Via Anagnina, Roma",
        "incident_lat": 41.8480,
        "incident_lng": 12.5765,
        "incident_description": (
            "14:12 local time. Aurora Martini's VW Golf entered the T-junction with right-"
            "of-way when a Peugeot 208 failed to yield from the left, striking the driver-"
            "side B-pillar at 35 km/h relative. 3.0 g lateral. Side curtain airbag "
            "(driver side) deployed. ESC activated post-impact to stabilise the vehicle. "
            "Martini reports mild bruising only. Third party at fault per dashcam evidence "
            "from the BMW behind. RESOLVED: claim approved €3,200, vehicle returned to "
            "service after 8 working days at officina Service Rossi (Ancona network)."
        ),
        "ai_damage_assessment_json": json.dumps({
            "areas": [
                {"area": "driver_door",          "severity": "severe",   "action": "replace"},
                {"area": "b_pillar_left",        "severity": "moderate", "action": "repair_straighten"},
                {"area": "rocker_panel_l",       "severity": "moderate", "action": "paint"},
                {"area": "side_curtain_l",       "severity": "deployed", "action": "replace"},
                {"area": "driver_side_mirror",   "severity": "severe",   "action": "replace"},
                {"area": "rear_door_left",       "severity": "minor",    "action": "paint"},
            ],
            "structural_damage": False,
            "drivable": True,
        }),
        "assigned_adjuster": "Stefano Romano",
    },
    "CASE-2025-00045": {
        "incident_location": "SP 35 — 4 km north of Saronno",
        "incident_lat": 45.6480,
        "incident_lng": 9.0200,
        "incident_description": (
            "21:38 local time, dark + wet road surface. Monica Rinaldi's BMW X5 was "
            "struck head-on by an oncoming Renault Captur that crossed into the opposite "
            "lane after the driver allegedly fell asleep. Combined closing speed ~110 km/h. "
            "Both vehicles' front + knee airbags deployed. ABS engaged 0.4 s before "
            "impact. Rinaldi released after Pronto Soccorso checkup (minor lacerations); "
            "other driver remains hospitalised — Carabinieri investigation ongoing. Initial "
            "fraud-risk reading 42% pending toxicology results on the other driver."
        ),
        "ai_damage_assessment_json": json.dumps({
            "areas": [
                {"area": "front_bumper",       "severity": "destroyed", "action": "replace"},
                {"area": "hood",               "severity": "destroyed", "action": "replace"},
                {"area": "front_fender_l",     "severity": "severe",    "action": "replace"},
                {"area": "front_fender_r",     "severity": "severe",    "action": "replace"},
                {"area": "front_subframe",     "severity": "moderate",  "action": "straighten"},
                {"area": "radiator_assembly",  "severity": "destroyed", "action": "replace"},
                {"area": "engine_mounts",      "severity": "moderate",  "action": "replace"},
                {"area": "windshield",         "severity": "severe",    "action": "replace"},
                {"area": "front_airbag_driver",   "severity": "deployed", "action": "replace"},
                {"area": "front_airbag_passenger","severity": "deployed", "action": "replace"},
                {"area": "knee_airbag_driver",    "severity": "deployed", "action": "replace"},
                {"area": "knee_airbag_passenger", "severity": "deployed", "action": "replace"},
                {"area": "headlight_xenon_l",  "severity": "destroyed", "action": "replace"},
                {"area": "headlight_xenon_r",  "severity": "destroyed", "action": "replace"},
            ],
            "structural_damage": True,
            "drivable": False,
        }),
        "assigned_adjuster": "Elena Ricci",
    },
}


# ────────────────────────────────────────────────────────────────────────────
# Photo catalogue — 3 images per case, registered in investigation_photos.
# Files live under website/static/img/investigations/<filename>; the UI shows
# a "Photo not found" placeholder until the actual JPGs are dropped in.
# ────────────────────────────────────────────────────────────────────────────

_PHOTO_CATALOGUE: dict[str, list[tuple[str, str, str]]] = {
    "CASE-2024-00142": [
        ("case-2024-00142-1.jpg",
         "Front quarter view from passenger side — crumpled hood and grille after intersection collision",
         "damage"),
        ("case-2024-00142-2.jpg",
         "Driver-side interior — deployed front airbag, fragmented windshield, deformed steering wheel",
         "damage"),
        ("case-2024-00142-3.jpg",
         "Intersection wide-angle — skid marks ending at impact point with traffic light visible",
         "scene"),
    ],
    "CASE-2024-00287": [
        ("case-2024-00287-1.jpg",
         "Rear bumper close-up — DHL van impact crumple zone, paint transfer visible",
         "damage"),
        ("case-2024-00287-2.jpg",
         "Tailgate gap measurement — uneven panel alignment after low-speed rear-end",
         "damage"),
        ("case-2024-00287-3.jpg",
         "Highway shoulder scene — Tesla and DHL van photographed by Carabinieri on Tangenziale",
         "scene"),
    ],
    "CASE-2024-00391": [
        ("case-2024-00391-1.jpg",
         "Catastrophic front-end damage — hood folded back to windshield, lights detached",
         "damage"),
        ("case-2024-00391-2.jpg",
         "Removed front brake pads with worn-through friction material + grooved disc — metal-on-metal",
         "evidence"),
        ("case-2024-00391-3.jpg",
         "Driver-app screen — log of 6 dismissed BRAKE WEAR CRITICAL alerts in the prior 14 days",
         "evidence"),
    ],
    "CASE-2025-00012": [
        ("case-2025-00012-1.jpg",
         "Driver-side door + B-pillar damage after T-junction side impact",
         "damage"),
        ("case-2025-00012-2.jpg",
         "Other vehicle (Peugeot 208) at scene with right-of-way infraction angle",
         "scene"),
        ("case-2025-00012-3.jpg",
         "Dashcam frame from BMW behind — Peugeot failing to yield at the junction",
         "evidence"),
    ],
    "CASE-2025-00045": [
        ("case-2025-00045-1.jpg",
         "BMW X5 frontal damage — bumper destroyed, hood crumpled, radiator visible",
         "damage"),
        ("case-2025-00045-2.jpg",
         "Wet provincial road at night — skid marks and impact debris field",
         "scene"),
        ("case-2025-00045-3.jpg",
         "Post-recovery front section — clear view of structural deformation requiring chassis-bench work",
         "damage"),
    ],
}


def _enrich_investigations(conn) -> int:
    """Overwrite descriptions / damage-assessment / adjuster on every boot."""
    cursor = conn.cursor()
    n = 0
    for case_no, fields in _ENRICHMENTS.items():
        # Only touch rows that actually exist (the seed may not have run yet).
        exists = cursor.execute(
            "SELECT 1 FROM investigations WHERE case_number=?", (case_no,)
        ).fetchone()
        if not exists:
            continue
        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [case_no]
        cursor.execute(
            f"UPDATE investigations SET {set_clause}, updated_at=CURRENT_TIMESTAMP "
            f"WHERE case_number=?",
            values,
        )
        n += cursor.rowcount
    conn.commit()
    return n


def _seed_photos(conn) -> int:
    """Register the canonical photo set per investigation (idempotent)."""
    cursor = conn.cursor()
    # Ensure the (case_number, filename) uniqueness so INSERT OR IGNORE works.
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_inv_photos_case_filename "
        "ON investigation_photos(case_number, filename)"
    )
    inserted = 0
    for case_no, photos in _PHOTO_CATALOGUE.items():
        for filename, caption, photo_type in photos:
            cursor.execute(
                "INSERT OR IGNORE INTO investigation_photos "
                "(case_number, filename, caption, photo_type) VALUES (?,?,?,?)",
                (case_no, filename, caption, photo_type),
            )
            inserted += cursor.rowcount
    conn.commit()
    return inserted


def migrate_and_seed():
    """Run migrations + seed + enrich demo investigations. Safe on every boot."""
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()

    # 1. Column migrations — swallow "duplicate column" errors so the script is idempotent.
    for sql in _INVESTIGATION_MIGRATIONS:
        try:
            cursor.execute(sql)
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                raise

    # 2. Photo table + unique index on (case_number, filename) (rebuilt below if needed).
    cursor.execute(_INVESTIGATION_PHOTOS_DDL)
    try:
        cursor.execute(_UNIQUE_CASE_INDEX_DDL)
    except sqlite3.IntegrityError:
        pass

    conn.commit()

    # 3. Demo cases (first-time INSERT path).
    seeded = _seed_investigations(conn)
    if seeded:
        print(f"🌱 Seeded {seeded} demo investigations into cyclesync.db.")

    # 4. Enrich with rich narratives + structured damage assessments.
    enriched = _enrich_investigations(conn)
    if enriched:
        print(f"📝 Enriched {enriched} investigation(s) with narrative + damage_assessment.")

    # 5. Register the canonical photo set.
    photos_added = _seed_photos(conn)
    if photos_added:
        total = sum(len(v) for v in _PHOTO_CATALOGUE.values())
        print(f"📷 Registered {photos_added} new photos "
              f"({total} canonical across {len(_PHOTO_CATALOGUE)} cases).")

    conn.close()


if __name__ == "__main__":
    migrate_and_seed()
