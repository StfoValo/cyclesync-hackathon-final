from mcp_agent_server.core_llm_client import CoreLLMClient
from mcp_agent_server.prompts.actuary_prompt import get_actuary_system_prompt, get_actuary_user_prompt
import time

class AIOrchestrator:
    def __init__(self):
        self.llm_client = CoreLLMClient()

    def run_actuarial_strategy_analysis(self, json_payload: str, region: str): # <-- ADDED REGION
        yield f"### 🔄 Unipol Enterprise AI Initialization\n"
        yield f"Ingesting regional VSI telemetry, predictive hardware risk, and network capacity...\n\n"
        time.sleep(0.5)
        
        system_instruction = get_actuary_system_prompt()
        user_prompt = get_actuary_user_prompt(json_payload)
            
        # FIX: Passing 'region' to the LLM client
        for chunk in self.llm_client.stream_inference(system_instruction, user_prompt, region):
            yield chunk

    def run_circular_logistics_analysis(self, json_payload: str, region: str): # <-- ADDED REGION
        yield f"### 🔄 CycleSync Reverse Logistics Engine\n"
        yield f"Ingesting End-of-Life (EOL) component volumes and cross-referencing regional recycling hubs...\n\n"
        time.sleep(0.5)
        
        system_instruction = get_logistics_system_prompt()
        user_prompt = get_logistics_user_prompt(json_payload)
        
        # FIX: Passing 'region' to the LLM client
        for chunk in self.llm_client.stream_inference(system_instruction, user_prompt, region):
            yield chunk
