import os
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from models.insurer_models.actuarial_model import ActuarialModel
from mcp_agent_server.ai_orchestrator import AIOrchestrator
from models.insurer_models.actuarial_model import ActuarialModel
from models.insurer_models.fleet_model import FleetModel

router = APIRouter()
orchestrator = AIOrchestrator()
actuarial_model = ActuarialModel()

@router.get("/api/ai/orchestrate/{region}")
async def orchestrate_ai(request: Request, region: str): 
    client_ip = request.client.host
    print(f"🧠 USER {client_ip} triggered AI Strategy for region: {region}")
    
    portfolio = get_cache('asset_risk_portfolio')
    region_data = next((r for r in portfolio.get("regional", []) if r["region"] == region), None)
    
    payload = json.dumps(region_data) if region_data else f'{{"region": "{region}", "status": "no data"}}'
    
    def generate():
        for chunk in orchestrator.run_actuarial_strategy_analysis(payload, region):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/api/ai/circular-logistics/{region}")
async def orchestrate_circular_logistics(region: str):
    
    payload = build_reverse_logistics_payload(region)
    
    def generate():
        for chunk in orchestrator.run_circular_logistics_analysis(payload, region):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


def build_reverse_logistics_payload(target_region: str) -> str:
    """
    Creates a hyper-local ESG routing payload for the AI using cached data.
    Gracefully handles regions that might not have BEV telemetry.
    """
    # 1. Fetch Actuarial Risk Portfolio (Tires & Brakes) from Cache
    portfolio = get_cache('asset_risk_portfolio')
    region_actuarial = next((r for r in portfolio.get("regional", []) if r["region"] == target_region), None)

    # 2. Fetch BEV Telemetry from Cache
    bev_analytics = get_cache('bev_regional_analytics')
    region_bev = next((r for r in bev_analytics if r["region_name"] == target_region), None)

    # 3. Check for core Actuarial data
    if not region_actuarial:
        return json.dumps({"error": f"Insufficient actuarial data to run logistics for {target_region}"})

    # --- FIX: Gracefully default BEV volumes to 0 if the region has no electric cars! ---
    bev_volumes = region_bev['cohorts']['0-3_months'] if region_bev else 0

    # 4. Define Regional Recycling Hubs
    recycling_hubs = [
        {"Name": f"Cobat Battery Extraction Center ({target_region})", "Specialty": "Black Mass Recycling"},
        {"Name": f"Enel X 2nd-Life Hub ({target_region})", "Specialty": "Grid Storage Repurposing"},
        {"Name": f"Ecopneus Rubber Granulate Plant", "Specialty": "Asphalt Recycling"},
        {"Name": f"Fonderie Metallurgiche Nord", "Specialty": "Scrap Metal Smelting"}
    ]

    # 5. Construct the Payload
    payload = {
        "Target_Region": target_region,
        "End_Of_Life_Volumes": {
            "Brake_Pads": region_actuarial['brakes'][2], 
            "Tires": region_actuarial['tires'][2],       
            "EV_Batteries": bev_volumes 
        },
        "Available_Recycling_Hubs": recycling_hubs
    }

    return json.dumps(payload, indent=2)
