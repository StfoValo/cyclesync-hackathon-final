from mcp_agent_server.core_llm_client import CoreLLMClient
from mcp_agent_server.prompts.actuary_prompt import get_actuary_system_prompt, get_actuary_user_prompt
import time

class AIOrchestrator:
    def __init__(self):
        self.llm_client = CoreLLMClient()

    def run_actuarial_strategy_analysis(self, json_payload: str):
        """Handles the VSI and Repair Network orchestration analysis."""
        
        # 1. Terminal Boot Sequence (UI Polish)
        yield f"### 🔄 Unipol Enterprise AI Initialization\n"
        yield f"Ingesting regional VSI telemetry, predictive hardware risk, and network capacity...\n\n"
        time.sleep(0.5)
        
        # 2. Build the Prompts
        system_instruction = get_actuary_system_prompt()
        user_prompt = get_actuary_user_prompt(json_payload)
        
        # 3. Stream the AI Response from Gemini
        for chunk in self.llm_client.stream_inference(system_instruction, user_prompt):
            yield chunk
