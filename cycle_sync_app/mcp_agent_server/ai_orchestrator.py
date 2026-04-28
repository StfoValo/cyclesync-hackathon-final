from mcp_agent_server.core_llm_client import CoreLLMClient
from mcp_agent_server.prompts.oem_battery_prompt import get_oem_system_prompt, get_oem_user_prompt
from models.data_manager.market_cache_manager import MarketCacheManager
import time

class AIOrchestrator:
    def __init__(self):
        self.llm_client = CoreLLMClient()

    def run_recycler_analysis(self, sector, quantity, platform_value):
        """Handles the legacy Recycler Market Analysis feature."""
        yield f"### 🔍 CycleSync Agent Initialization\n"
        yield f"Analyzing local network data and scanning global market feeds for **{sector.upper()}**...\n\n"
        time.sleep(0.5)
        
        cached_context = MarketCacheManager.get_recent_context(sector)
        yield f"### 📚 Ingested Market Sources\n"
        
        clean_context = ""
        for line in cached_context.split('\n'):
            if line.strip():
                clean_line = line.replace("*", "").strip()
                clean_context += clean_line + "\n"
                yield f"> {clean_line}\n\n"
                time.sleep(0.1)
                
        yield f"---\n### 🧠 AI Market Strategy\n"
        time.sleep(0.5)
        
        system_instruction = get_recycler_system_prompt()
        user_prompt = get_recycler_user_prompt(sector, quantity, platform_value, clean_context)
        
        for chunk in self.llm_client.stream_inference(system_instruction, user_prompt):
            yield chunk

    # --- THE NEW OEM BATTERY ROUTE ---
    def run_oem_battery_analysis(self, json_payload: str):
        """Handles the large-scale OEM Battery Supply Chain Analysis."""
        yield f"### 🔄 CycleSync Enterprise AI Initialization\n"
        yield f"Ingesting regional battery telemetry and calculating EOL logistics...\n\n"
        time.sleep(0.5)
        
        # 1. Build the Prompts
        system_instruction = get_oem_system_prompt()
        user_prompt = get_oem_user_prompt(json_payload)
        
        # 2. Stream the response from the Core Client
        for chunk in self.llm_client.stream_inference(system_instruction, user_prompt):
            yield chunk