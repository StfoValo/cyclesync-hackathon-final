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


class RepairQuoteRequest(BaseModel):
    component_id: str
    issue_description: str
    wear_level: str
    shop_name: str      # <-- NEW
    driver_name: str    # <-- NEW
    language: str = "en"



# Add the endpoint
@router.post("/api/ai/repair-quote")
async def generate_repair_quote(request: RepairQuoteRequest):
    print(f"🛠️ Triggering AI Repair Quote for: {request.component_id}")
    
    # Bundle the incoming frontend data into the JSON payload
    context_payload = json.dumps({
        "component_id": request.component_id,
        "issue_description": request.issue_description,
        "wear_level": request.wear_level
    })
    
    response_generator = orchestrator.run_repair_quote_generation(
        json_payload=context_payload,
        component_id=request.component_id,
        shop_name=request.shop_name,
        driver_name=request.driver_name,
        lang=request.language
    )
    
    return StreamingResponse(response_generator, media_type="text/plain")