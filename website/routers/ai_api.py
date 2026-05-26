import os
import json
import sqlite3
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from mcp_agent_server.ai_orchestrator import AIOrchestrator

router = APIRouter()

# Instantiate Stefano's Orchestrator
orchestrator = AIOrchestrator()

# ==========================================
# HELPER: Bulletproof Local Cache Reader
# ==========================================
def get_cache(key: str):
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui_cache.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT json_data FROM api_cache WHERE endpoint_key=?", (key,))
        row = cursor.fetchone()
        conn.close()
        return json.loads(row[0]) if row else {}
    except Exception as e:
        print(f"⚠️ Cache read error: {e}")
        return {}

# ==========================================
# PIPELINE 1: Executive Risk Chat (Deterministic)
# ==========================================
class PredefinedChatRequest(BaseModel):
    question_id: str
    question_text: str
    language: str = "en"

@router.post("/api/ai/ask-predefined")
async def ask_predefined_endpoint(request: PredefinedChatRequest):
    """Handles predefined button clicks and feeds exact cache data to Groq."""
    
    # Map the Question ID to the correct Database Cache
    if request.question_id in ["exec_reg_1", "exec_reg_2"]:
        context_data = get_cache('fleet_regional_kpis')
    elif request.question_id in ["exec_demo_1", "exec_demo_2"]:
        context_data = get_cache('demographic_deep_dive')
    elif request.question_id in ["exec_asset_1", "exec_asset_2"]:
        context_data = get_cache('asset_risk_portfolio')
    else:
        context_data = {"status": "No specific data required."}

    # Convert the dictionary back to a JSON string for the prompt
    json_payload = json.dumps(context_data)
    
    # Call the orchestrator to stream the LLM response
    response_generator = orchestrator.run_predefined_risk_query(
        question_id=request.question_id,
        question_text=request.question_text,
        json_payload=json_payload,
        lang=request.language
    )
    
    return StreamingResponse(response_generator, media_type="text/plain")
    
# ==========================================
# PIPELINE 2: AI Routing Strategy (Groq/Gemini Streaming)
# ==========================================
@router.get("/api/ai/orchestrate/{region}")
async def orchestrate_ai(request: Request, region: str, lang: str = "en"): 
    """Handles the 'Run AI Strategy' button in the AI Route tab"""
    client_ip = request.client.host
    print(f"🧠 USER {client_ip} triggered AI Strategy for region: {region} (Lang: {lang})")
    
    # 1. Fetch real live data from your cache
    fleet_data = get_cache('fleet_data')
    asset_risk = get_cache('asset_risk_global')
    
    # 2. Combine into payload
    context_payload = json.dumps({
        "target_region": region,
        "fleet_metrics": fleet_data,
        "risk_metrics": asset_risk
    })
    
    # 3. Call orchestrator
    response_generator = orchestrator.run_actuarial_strategy_analysis(
        json_payload=context_payload, 
        region=region, 
        lang=lang
    )
    
    # 4. Stream response
    return StreamingResponse(response_generator, media_type="text/plain")

# ==========================================
# PIPELINE 3: ESG & Circular Logistics (Groq/Gemini Streaming)
# ==========================================
@router.get("/api/ai/circular-logistics/{component_type}")
async def circular_logistics_ai(request: Request, component_type: str, lang: str = "en"):
    """Handles the 'Run Component Triage' button in the ESG tab"""
    print(f"♻️ Triggering AI Logistics for component: {component_type}")
    
    esg_data = get_cache('esg_metrics')
    
    context_payload = json.dumps({
        "component": component_type,
        "esg_telemetry": esg_data
    })
    
    response_generator = orchestrator.run_circular_logistics_analysis(
        json_payload=context_payload,
        region="Italy",
        lang=lang
    )

    return StreamingResponse(response_generator, media_type="text/plain")


# ==========================================
# PIPELINE 4: AI Batch Recycling (ESG → AI Triage & Recycling sub-tab)
# Streams an analysis of every stocked component in the given category.
# ==========================================
@router.get("/api/ai/batch-recycling/{category}")
async def ai_batch_recycling(category: str, lang: str = "en"):
    """Circular-economy batch analysis for stocked components.

    Category: 'tire', 'brake_pad', 'ev_battery', or 'all'.
    """
    print(f"♻️ [API HIT] /api/ai/batch-recycling/{category} (lang={lang})")
    from models.data_manager.database_manager import DatabaseManager

    conn = DatabaseManager.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if category == "all":
        rows = cursor.execute(
            """
            SELECT c.*, v.plate_number FROM components c
            LEFT JOIN vehicles v ON c.vehicle_vin = v.vin
            WHERE c.status = 'stocked'
            ORDER BY c.category, c.wear_percent DESC
            """
        ).fetchall()
    else:
        rows = cursor.execute(
            """
            SELECT c.*, v.plate_number FROM components c
            LEFT JOIN vehicles v ON c.vehicle_vin = v.vin
            WHERE c.status = 'stocked' AND c.category = ?
            ORDER BY c.wear_percent DESC
            """,
            (category,),
        ).fetchall()
    conn.close()

    components = [dict(r) for r in rows]
    if not components:
        def _empty():
            yield "⚠️ No stocked components found for this category."
        return StreamingResponse(_empty(), media_type="text/plain")

    total_count = len(components)
    total_recovery_value = sum(c.get("recovery_value_eur") or 0 for c in components)
    total_co2_saved = sum(c.get("co2_saved_kg") or 0 for c in components)
    avg_wear = sum(c.get("wear_percent") or 0 for c in components) / total_count

    by_category: dict = {}
    for c in components:
        cat = c["category"]
        bucket = by_category.setdefault(
            cat, {"count": 0, "items": [], "total_value": 0, "total_co2": 0}
        )
        bucket["count"] += 1
        bucket["total_value"] += c.get("recovery_value_eur") or 0
        bucket["total_co2"] += c.get("co2_saved_kg") or 0
        bucket["items"].append({
            "serial": c.get("serial_number"),
            "brand": c.get("brand", "Unknown"),
            "model": c.get("model_name", ""),
            "wear_pct": c.get("wear_percent", 0),
            "current_recommendation": c.get("ai_recommendation", "None"),
            "current_value_eur": c.get("recovery_value_eur"),
            "co2_saved_kg": c.get("co2_saved_kg"),
            "facility": c.get("destination_facility"),
            "specs": json.loads(c["specs_json"]) if c.get("specs_json") else {},
            "from_vehicle": c.get("plate_number", "Unknown"),
        })

    payload = json.dumps({
        "batch_summary": {
            "total_components": total_count,
            "categories": {k: v["count"] for k, v in by_category.items()},
            "average_wear_pct": round(avg_wear, 1),
            "current_total_recovery_value_eur": round(total_recovery_value, 2),
            "current_total_co2_saved_kg": round(total_co2_saved, 1),
        },
        "components_by_category": by_category,
    }, indent=2)

    category_label = {
        "tire": "Tires",
        "brake_pad": "Brake Pads",
        "ev_battery": "EV Batteries",
        "all": "All Categories",
    }
    cat_name = category_label.get(category, category)
    language = "Italian" if lang == "it" else "English"

    system_prompt = (
        "You are the VeriTwin Circular Economy AI, an expert in automotive component "
        "recycling, second-life allocation, and ESG revenue optimization.\n\n"
        f"You are analyzing a BATCH of {total_count} stocked components ({cat_name}) "
        "for optimal recycling/reuse strategy.\n\n"
        "## SECTION 1: BATCH OVERVIEW & CONDITION ASSESSMENT\n"
        "Analyze wear percentages, brands, and specifications. Group components by\n"
        "condition tier (low wear = resell/reuse, medium = refurbish, high = recycle).\n\n"
        "## SECTION 2: OPTIMAL RECYCLING & REUSE STRATEGY\n"
        "For each tier, recommend the best pathway:\n"
        "- **Resell / Second-Life** (<50% wear) — estimate market resale price\n"
        "- **Retread / Refurbish** (50-75% wear) — refurbishment cost + revenue\n"
        "- **Recycle / Extract** (>75% wear) — material extraction revenue\n\n"
        "## SECTION 3: REVENUE PROJECTION\n"
        f"Provide an EUR breakdown vs the current individual estimate of €{round(total_recovery_value, 2)}.\n"
        "Indicate whether batch processing improves yield, and recommend facilities.\n\n"
        "## SECTION 4: ENVIRONMENTAL IMPACT\n"
        f"Current CO₂ saved: {round(total_co2_saved, 1)} kg. Add equivalents (trees, km offset)\n"
        "and ESG-disclosure-ready summary.\n\n"
        "## SECTION 5: ACTIONABLE NEXT STEPS\n"
        "A concrete 3-step plan with timelines and facility assignments.\n\n"
        "Use tables and bold numbers for key metrics. Be specific with EUR amounts.\n"
        f"RESPOND ENTIRELY IN {language}."
    )

    def _generate():
        if lang == "it":
            yield "### 🔄 VeriTwin Circular Economy AI — Analisi Batch\n"
            yield f"Analisi di **{total_count}** componenti ({cat_name}) in stock per strategia ottimale di riciclo/riutilizzo...\n\n"
        else:
            yield "### 🔄 VeriTwin Circular Economy AI — Batch Analysis\n"
            yield f"Analyzing **{total_count}** stocked components ({cat_name}) for optimal recycling/reuse strategy...\n\n"

        import time as _time
        _time.sleep(0.3)
        for chunk in orchestrator.llm_client.stream_inference(
            system_prompt, payload, f"batch_{category}", lang
        ):
            yield chunk

    return StreamingResponse(_generate(), media_type="text/plain")


# ==========================================
# PIPELINE 5: Anti-Fraud Adjuster AI (Investigation deep analysis)
# Streamed by the Adjuster portal's "AI Analysis" tab.
# ==========================================
def _summarize_window(samples):
    """Compress the 121 ±5-min samples into key markers + 12 downsampled snapshots.

    Goal: keep the LLM context compact (under ~3 KB) while still giving
    the AI a clear before / at / after view it can cite by timestamp.
    """
    if not samples:
        return None

    rows = [dict(r) for r in samples]
    by_t  = {r["seconds_relative"]: r for r in rows}

    # 1. Event-flag transitions (e.g. "ldw_alert", "abs_engaged", "IMPACT", "airbag_deployed").
    events = []
    last_flag = None
    for r in rows:
        flag = r.get("event_flag")
        if flag and flag != last_flag and flag != "normal":
            events.append({
                "t_sec": r["seconds_relative"],
                "flag":  flag,
                "speed_kmh": r.get("vehicle_speed_kmh"),
            })
            last_flag = flag

    # 2. Downsample to 12 meaningful timestamps spanning the window.
    keys = [-300, -180, -120, -60, -30, -10, -5, 0, 5, 30, 120, 300]
    snapshots = []
    for k in keys:
        r = by_t.get(k)
        if not r:
            continue
        snapshots.append({
            "t_sec":                  r["seconds_relative"],
            "vehicle_speed_kmh":      r.get("vehicle_speed_kmh"),
            "accel_x_g":              r.get("accel_x_g"),
            "accel_y_g":              r.get("accel_y_g"),
            "accel_total_g":          r.get("accel_total_g"),
            "gyro_yaw_deg_s":         r.get("gyro_yaw_deg_s"),
            "brake_pressure_bar":     r.get("brake_pressure_bar"),
            "brake_pedal_pct":        r.get("brake_pedal_pct"),
            "throttle_position_pct":  r.get("throttle_position_pct"),
            "steering_angle_deg":     r.get("steering_angle_deg"),
            "abs_active":             r.get("abs_active"),
            "esc_active":             r.get("esc_active"),
            "airbag_deployed":        r.get("airbag_deployed"),
            "event_flag":             r.get("event_flag"),
        })

    return {
        "duration_seconds":   600,
        "resolution_seconds": 5,
        "events_in_order":    events,
        "snapshots":          snapshots,
    }


@router.get("/api/ai/investigation/{case_number}")
async def ai_investigation_analysis(case_number: str, lang: str = "en"):
    """Streaming fraud + damage assessment for a single investigation."""
    print(f"🚦 [API HIT] /api/ai/investigation/{case_number} (lang={lang})")
    from models.data_manager.database_manager import DatabaseManager

    conn = DatabaseManager.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    inv = cursor.execute(
        """
        SELECT i.*, v.plate_number, v.driver_name,
               cm.model_name, cm.manufacturer, cm.powertrain
        FROM investigations i
        JOIN vehicles v        ON i.vehicle_vin = v.vin
        JOIN car_models cm     ON v.model_id    = cm.id
        WHERE i.case_number = ?
        """,
        (case_number,),
    ).fetchone()

    if not inv:
        conn.close()
        def _missing():
            yield f"⚠️ Investigation **{case_number}** not found."
        return StreamingResponse(_missing(), media_type="text/plain")

    telem = cursor.execute(
        "SELECT * FROM vehicle_telemetry WHERE vin = ?", (inv["vehicle_vin"],)
    ).fetchone()
    components = cursor.execute(
        "SELECT * FROM components WHERE vehicle_vin = ?",
        (inv["vehicle_vin"],),
    ).fetchall()
    photos = cursor.execute(
        "SELECT filename, caption, photo_type, uploaded_at "
        "FROM investigation_photos WHERE case_number = ? ORDER BY id",
        (case_number,),
    ).fetchall()
    maintenance = cursor.execute(
        "SELECT event_date, event_type, description, mileage_km, cost_eur, severity "
        "FROM maintenance_events WHERE vehicle_vin = ? "
        "ORDER BY event_date DESC LIMIT 10",
        (inv["vehicle_vin"],),
    ).fetchall()

    # ±5-minute locked telemetry window stored by the incident-telemetry seeder.
    incident_samples = cursor.execute(
        """SELECT seconds_relative, vehicle_speed_kmh, accel_x_g, accel_y_g,
                  accel_total_g, gyro_yaw_deg_s,
                  brake_pressure_bar, brake_pedal_pct, throttle_position_pct,
                  steering_angle_deg,
                  abs_active, esc_active, airbag_deployed,
                  event_flag
             FROM incident_telemetry_samples
            WHERE case_number = ?
            ORDER BY seconds_relative""",
        (case_number,),
    ).fetchall()
    conn.close()

    inv_data = dict(inv)
    tel_data = dict(telem) if telem else {}
    comp_data = [dict(c) for c in components]

    # Parse the structured damage assessment we seeded for this case (if any).
    damage_assessment = None
    if inv_data.get("ai_damage_assessment_json"):
        try:
            damage_assessment = json.loads(inv_data["ai_damage_assessment_json"])
        except Exception:
            damage_assessment = None
    # Same for the TPMS-at-impact snapshot.
    tpms_snapshot = None
    if inv_data.get("tpms_snapshot_json"):
        try:
            tpms_snapshot = json.loads(inv_data["tpms_snapshot_json"])
        except Exception:
            tpms_snapshot = inv_data["tpms_snapshot_json"]

    context = json.dumps({
        # ── Case identity ────────────────────────────────────────────────
        "case_number":         inv_data["case_number"],
        "vehicle":             f"{inv_data['manufacturer']} {inv_data['model_name']}",
        "plate":               inv_data["plate_number"],
        "powertrain":          inv_data.get("powertrain") or "unknown",
        "assigned_adjuster":   inv_data.get("assigned_adjuster"),

        # ── Incident snapshot (from investigations table) ────────────────
        "incident_type":         inv_data.get("incident_type"),
        "incident_date":         inv_data.get("incident_date"),
        "incident_location":     inv_data.get("incident_location"),
        "incident_description":  inv_data.get("incident_description"),
        "speed_at_impact_kmh":   inv_data.get("speed_at_impact"),
        "g_force_max":           inv_data.get("g_force_max"),
        "g_force_lateral":       inv_data.get("g_force_lateral"),
        "abs_triggered":         bool(inv_data.get("abs_triggered")) if inv_data.get("abs_triggered") is not None else None,
        "airbag_deployed":       bool(inv_data.get("airbag_deployed")) if inv_data.get("airbag_deployed") is not None else None,
        "coolant_temp_c":        inv_data.get("coolant_temp"),
        "fraud_risk_score":      inv_data.get("fraud_risk_score"),
        "priority":              inv_data.get("priority"),
        "status":                inv_data.get("status"),
        "tpms_at_impact":        tpms_snapshot,

        # ── Pre-built damage assessment (seeded — AI extends with costs) ─
        "initial_damage_assessment": damage_assessment,

        # ── Post-crash blackbox / OBD-II snapshot (live row) ─────────────
        "post_crash_telemetry": {
            "blackbox_event_type":   tel_data.get("blackbox_event_type"),
            "event_max_g":           tel_data.get("event_max_g"),
            "impact_severity":       tel_data.get("impact_severity"),
            "last_event_timestamp":  tel_data.get("last_event_timestamp"),
            "abs_active":            tel_data.get("abs_active"),
            "esc_active":            tel_data.get("esc_active"),
            "accel_x_g":             tel_data.get("accel_x_g"),
            "accel_y_g":             tel_data.get("accel_y_g"),
            "accel_z_g":             tel_data.get("accel_z_g"),
            "gyro_yaw_deg_s":        tel_data.get("gyro_yaw_deg_s"),
            "gps_lat":               tel_data.get("gps_lat"),
            "gps_lon":               tel_data.get("gps_lon"),
            "brake_pressure_bar":    tel_data.get("brake_pressure_bar"),
            "brake_pedal_pct":       tel_data.get("brake_pedal_pct"),
            "steering_angle_deg":    tel_data.get("steering_angle_deg"),
            "vehicle_speed_kmh":     tel_data.get("vehicle_speed_kmh"),
            "engine_rpm":            tel_data.get("engine_rpm"),
            "fuel_level_pct":        tel_data.get("fuel_level_pct"),
            "battery_soc_pct":       tel_data.get("battery_soc_pct"),
            "tpms_now": {
                "fl_bar": tel_data.get("tpms_fl_bar"), "fr_bar": tel_data.get("tpms_fr_bar"),
                "rl_bar": tel_data.get("tpms_rl_bar"), "rr_bar": tel_data.get("tpms_rr_bar"),
            },
        },

        # ── Driver-behaviour profile (telematics scoring) ───────────────
        "driver_profile": {
            "driving_score":         tel_data.get("driving_score"),
            "safety_score":          tel_data.get("safety_score"),
            "eco_score":             tel_data.get("eco_score"),
            "smoothness_score":      tel_data.get("smoothness_score"),
            "hard_brake_count":      tel_data.get("hard_brake_count"),
            "hard_accel_count":      tel_data.get("hard_accel_count"),
            "hard_cornering_count":  tel_data.get("hard_cornering_count"),
            "speeding_events_count": tel_data.get("speeding_events_count"),
            "harsh_event_count_24h": tel_data.get("harsh_event_count_24h"),
            "night_driving_pct":     tel_data.get("night_driving_pct"),
            "odometer_km":           tel_data.get("current_odometer_km"),
        },

        # ── Component wear at incident time (only > 50%) ────────────────
        "components_at_risk": [
            {
                "category":     c.get("category"),
                "position":     c.get("position"),
                "brand":        c.get("brand"),
                "wear_percent": c.get("wear_percent"),
                "status":       c.get("status"),
                "ai_recommendation": c.get("ai_recommendation"),
            }
            for c in comp_data if (c.get("wear_percent") or 0) > 50
        ],

        # ── Photographic evidence (filenames + captions) ────────────────
        "photos": [
            {"filename": p["filename"], "caption": p["caption"], "type": p["photo_type"]}
            for p in photos
        ],

        # ── Recent maintenance history (chronological context) ──────────
        "maintenance_history_last_10": [
            {
                "date":     m["event_date"],
                "type":     m["event_type"],
                "desc":     m["description"],
                "km":       m["mileage_km"],
                "cost_eur": m["cost_eur"],
                "severity": m["severity"],
            }
            for m in maintenance
        ],

        # ── Locked ±5-min telemetry window summary ───────────────────────
        # Full series is 121 samples; the AI gets (a) key event markers and
        # (b) downsampled snapshots so the prompt stays compact.
        "telemetry_window": _summarize_window(incident_samples),
    }, indent=2)

    language = "Italian" if lang == "it" else "English"
    system_prompt = (
        "You are the VeriTwin AI Insurance Adjuster — an expert anti-fraud and damage-"
        "assessment AI embedded in a fleet insurance platform.\n\n"
        "You receive a JSON context that combines THREE legally-sealed evidence "
        "streams, all locked to this case:\n"
        "  1. The reported incident narrative and the structured `initial_damage_"
        "     assessment` of affected vehicle areas.\n"
        "  2. `telemetry_window` — the immutable blackbox + OBD-II record from −300 s "
        "     to +300 s around the impact (events_in_order shows flag transitions "
        "     like `ldw_alert`, `FCW`, `abs_engaged`, `IMPACT`, `airbag_deployed`; "
        "     snapshots give downsampled readings at 12 timestamps).\n"
        "  3. `photos` — captioned forensic photographs taken on-scene and at the body "
        "     shop; treat the captions as ground-truth descriptions of what each "
        "     image shows.\n\n"
        "Your fraud reasoning MUST CROSS-REFERENCE all three streams. Quote the "
        "specific second-mark (e.g. \"at t=−5 s throttle was still 19 %\") and the "
        "specific photo caption when each one supports a finding.\n\n"
        "Context also includes (d) the post-crash live snapshot, (e) the driver-"
        "behaviour profile, and (f) maintenance history.\n\n"
        "Italian aftermarket reference rates to ground your estimates:\n"
        "  • General labour:         €65–€85/h\n"
        "  • Body / paint shop:      €90–€120/h\n"
        "  • Front bumper assembly:  €600–€1500 (mid) / €1500–€3000 (premium)\n"
        "  • Hood (steel / alu):     €800–€2200\n"
        "  • Windshield:             €600–€1200\n"
        "  • Headlight (LED/Xenon):  €400–€1600 each\n"
        "  • Airbag module + reset:  €1500–€3000 per airbag\n"
        "  • Radiator + AC condenser:€500–€1200 combined\n"
        "  • Front subframe:         €1200–€2500 (replace) / €500–€900 (straighten)\n"
        "  • B-pillar / door panel:  €900–€2400\n"
        "  • Brake pad + disc set:   €350–€700 per axle\n"
        "  • Chassis bench-time:     €120/h × 4–10 h for structural\n\n"
        "Produce THREE clearly-labelled sections:\n\n"
        "## SECTION 1 — FRAUD ANALYSIS\n"
        "Cross-check the reported narrative against telemetry. Cite SPECIFIC numbers "
        "(speed_at_impact_kmh, event_max_g, abs_triggered, airbag_deployed, harsh-event "
        "counters, component wear). Flag inconsistencies (e.g. low reported speed vs "
        "high g, dismissed maintenance alerts, prior harsh-event pattern). Conclude "
        "with a numeric fraud-risk reassessment (0-100) + justification.\n\n"
        "## SECTION 2 — DAMAGE ASSESSMENT & REPAIR ESTIMATE\n"
        "Walk through the `initial_damage_assessment.areas` list. For each area "
        "produce a row in a markdown table with: Area | Action (replace/repair/paint) | "
        "Parts EUR | Labour EUR | Subtotal EUR. Add separate lines for paint hours and "
        "chassis-bench time when structural damage is flagged. Sum to a **Total Repair "
        "Cost (EUR)** at the bottom. Reference the `photos` array by caption when "
        "evidence supports a specific cost (e.g. \"photo 1 shows hood fully folded → "
        "replace, not repair\").\n\n"
        "## SECTION 3 — VERDICT\n"
        "One of: ✅ APPROVE / ⚠️ PARTIALLY APPROVE / ❌ DENY (or in Italian: APPROVATA / "
        "PARZIALE / NEGATA). Provide 2–4 bullet-pointed justifications citing the "
        "specific data points that drove the decision. If denial is on negligence "
        "grounds (e.g. dismissed maintenance alerts), state that explicitly.\n\n"
        "Use markdown tables for the cost breakdown, **bold** for EUR totals, and emoji "
        "for visual urgency. Be specific with EUR amounts — no \"approximately\" hedge.\n"
        f"RESPOND ENTIRELY IN {language}."
    )

    def _generate():
        if lang == "it":
            yield "### 🔄 Inizializzazione VeriTwin Anti-Frode AI...\n"
            yield f"Analisi del caso **{case_number}** — Acquisizione telemetria, dati componenti e foto incidente...\n\n"
        else:
            yield "### 🔄 VeriTwin Anti-Fraud AI Initialization...\n"
            yield f"Analyzing case **{case_number}** — Ingesting telemetry, component data, and incident photos...\n\n"

        import time as _time
        _time.sleep(0.3)
        for chunk in orchestrator.llm_client.stream_inference(
            system_prompt, context, f"inv_{case_number}", lang
        ):
            yield chunk

    return StreamingResponse(_generate(), media_type="text/plain")


# ==========================================
# PIPELINE 6: Driver SOS (Emergency Response AI)
# Streamed by the driver app's red SOS button.
# ==========================================
@router.get("/api/ai/sos/{vin}")
async def ai_sos_analysis(vin: str, lang: str = "en"):
    """Streaming SOS analysis — classifies severity and dispatches help."""
    print(f"🆘 [API HIT] /api/ai/sos/{vin} (lang={lang})")
    from models.data_manager.database_manager import DatabaseManager

    conn = DatabaseManager.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    v = cursor.execute(
        """
        SELECT v.*, cm.model_name, cm.manufacturer
        FROM vehicles v JOIN car_models cm ON v.model_id = cm.id
        WHERE v.vin = ?
        """,
        (vin,),
    ).fetchone()
    t = cursor.execute(
        "SELECT * FROM vehicle_telemetry WHERE vin = ?", (vin,)
    ).fetchone()
    comps = cursor.execute(
        "SELECT category, position, wear_percent FROM components "
        "WHERE vehicle_vin = ? AND status = 'installed'",
        (vin,),
    ).fetchall()
    conn.close()

    if not v:
        def _missing():
            yield f"⚠️ Vehicle **{vin}** not found."
        return StreamingResponse(_missing(), media_type="text/plain")

    v_d = dict(v)
    t_d = dict(t) if t else {}

    context = json.dumps({
        "vehicle":            f"{v_d.get('manufacturer','')} {v_d.get('model_name','')}",
        "plate":              v_d.get("plate_number"),
        "driver":             v_d.get("driver_name"),
        "color":              v_d.get("color"),
        "region":             v_d.get("region_name"),
        "city":               v_d.get("city"),
        "odometer_km":        t_d.get("current_odometer_km", 0),
        "driving_score":      t_d.get("driving_score"),
        "has_blackbox":       bool(v_d.get("has_blackbox")) if v_d.get("has_blackbox") is not None else False,
        "gps":                {"lat": v_d.get("lat"), "lon": v_d.get("lon")},
        "critical_components":[
            {"category": c["category"], "position": c["position"], "wear": c["wear_percent"]}
            for c in comps if (c["wear_percent"] or 0) > 75
        ],
        "policy_number":      v_d.get("policy_number"),
        "policy_type":        v_d.get("policy_type"),
        "insurer":            v_d.get("insurer"),
    }, indent=2)

    language = "Italian" if lang == "it" else "English"
    system_prompt = (
        "You are the VeriTwin Emergency Response AI. The driver has just pressed the SOS button.\n\n"
        "Analyse the vehicle's current state and dispatch the appropriate response:\n\n"
        "## 1. SITUATION ASSESSMENT\n"
        "Score severity using telemetry, location and component health.\n"
        "Classify as MINOR (roadside assist), MODERATE (tow truck) or SEVERE (emergency services).\n\n"
        "## 2. INTERVENTION DISPATCH\n"
        "- MINOR: 🔧 Roadside assistance — flat tyre, minor mechanical, DTC codes\n"
        "- MODERATE: 🚗 Tow truck + mechanic — immobilised vehicle, critical component failure\n"
        "- SEVERE: 🚑 Ambulance + 🚔 Police + 🚗 Tow — suspected crash, airbag triggers, extreme G-forces\n\n"
        "## 3. INSURANCE NOTIFICATION\n"
        "Draft the alert sent to the insurer: policy number, location, severity, estimated cost.\n\n"
        "## 4. DRIVER INSTRUCTIONS\n"
        "Clear, calm instructions while help is en route.\n\n"
        "Use emoji for visual urgency. Be decisive and specific.\n"
        f"RESPOND ENTIRELY IN {language}."
    )

    def _generate():
        plate = v_d.get("plate_number") or vin[:8]
        if lang == "it":
            yield "### 🆘 VeriTwin Emergency AI — Attivato\n"
            yield f"Analisi veicolo **{plate}** in corso...\n\n"
        else:
            yield "### 🆘 VeriTwin Emergency AI — Activated\n"
            yield f"Analyzing vehicle **{plate}**...\n\n"

        import time as _time
        _time.sleep(0.3)
        for chunk in orchestrator.llm_client.stream_inference(
            system_prompt, context, f"sos_{vin}", lang
        ):
            yield chunk

    return StreamingResponse(_generate(), media_type="text/plain")


# ==========================================
# PIPELINE 7: AI Repair Quote (Driver app → Affiliated workshop popup)
# Pulled from upstream "AI feature on user app" commits.
# ==========================================
class RepairQuoteRequest(BaseModel):
    component_id: str
    issue_description: str
    wear_level: str
    shop_name: str
    driver_name: str
    language: str = "en"


@router.post("/api/ai/repair-quote")
async def generate_repair_quote(request: RepairQuoteRequest):
    """Streams an AI-drafted repair quote from a specific affiliated workshop."""
    print(f"🛠️ Triggering AI Repair Quote for: {request.component_id}")

    context_payload = json.dumps({
        "component_id": request.component_id,
        "issue_description": request.issue_description,
        "wear_level": request.wear_level,
    })

    response_generator = orchestrator.run_repair_quote_generation(
        json_payload=context_payload,
        component_id=request.component_id,
        shop_name=request.shop_name,
        driver_name=request.driver_name,
        lang=request.language,
    )

    return StreamingResponse(response_generator, media_type="text/plain")