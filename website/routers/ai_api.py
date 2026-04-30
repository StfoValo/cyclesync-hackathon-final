from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.insurer_models.actuarial_model import ActuarialModel
from mcp_agent_server.ai_orchestrator import AIOrchestrator
import json

router = APIRouter()
orchestrator = AIOrchestrator()
actuarial_model = ActuarialModel()

@router.get("/api/ai/orchestrate/{region}")
async def orchestrate_ai(region: str):
    # Fetch portfolio to feed into prompt
    portfolio = actuarial_model.get_asset_risk_portfolio()
    region_data = next((r for r in portfolio.get("regional", []) if r["region"] == region), None)
    
    payload = json.dumps(region_data) if region_data else f'{{"region": "{region}", "status": "no data"}}'
    
    def generate():
        for chunk in orchestrator.run_actuarial_strategy_analysis(payload):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")
