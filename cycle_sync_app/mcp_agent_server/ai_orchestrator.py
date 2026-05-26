from mcp_agent_server.core_llm_client import CoreLLMClient
from .prompts.actuary_prompt import get_actuary_system_prompt, get_actuary_user_prompt
from .prompts.reverse_logistics_prompt import get_logistics_system_prompt, get_logistics_user_prompt
from .prompts.risk_prompt import get_risk_system_prompt, get_risk_user_prompt
from .prompts.repair_prompt import get_repair_system_prompt, get_repair_user_prompt
import time

class AIOrchestrator:
    def __init__(self):
        self.llm_client = CoreLLMClient()

    def run_actuarial_strategy_analysis(self, json_payload: str, region: str, lang: str = "en"): 
        if lang == "it":
            yield f"### 🔄 Inizializzazione AI Enterprise CycleSync\n"
            yield f"Acquisizione telemetria VSI regionale, rischio hardware predittivo e capacità di rete...\n\n"
        else:
            yield f"### 🔄 CycleSync Enterprise AI Initialization\n"
            yield f"Ingesting regional VSI telemetry, predictive hardware risk, and network capacity...\n\n"
            
        time.sleep(0.5)
        
        system_instruction = get_actuary_system_prompt()
        if lang == "it":
            system_instruction += "\n\nIMPORTANT: You MUST generate your ENTIRE response in fluent Italian."

        else:
            system_instruction += "\n\nIMPORTANT: You MUST generate your ENTIRE response in English."

            
        user_prompt = get_actuary_user_prompt(json_payload)
            
        for chunk in self.llm_client.stream_inference(system_instruction, user_prompt, region, lang):
            yield chunk

    def run_circular_logistics_analysis(self, json_payload: str, region: str, lang: str = "en"): 
        if lang == "it":
            yield f"### 🔄 Motore Logistica Inversa CycleSync\n"
            yield f"Acquisizione volumi componenti di fine vita (EOL) e ricerca di hub di riciclaggio regionali...\n\n"
        else:
            yield f"### 🔄 CycleSync Reverse Logistics Engine\n"
            yield f"Ingesting End-of-Life (EOL) component volumes and cross-referencing regional recycling hubs...\n\n"
            
        time.sleep(0.5)
        
        system_instruction = get_logistics_system_prompt()
        if lang == "it":
            system_instruction += "\n\nIMPORTANT: You MUST generate your ENTIRE response in fluent Italian."
        else:
            system_instruction += "\n\nIMPORTANT: You MUST generate your ENTIRE response in English."
            
        user_prompt = get_logistics_user_prompt(json_payload)
        
        for chunk in self.llm_client.stream_inference(system_instruction, user_prompt, region, lang):
            yield chunk

    def run_predefined_risk_query(self, question_id: str, question_text: str, json_payload: str, lang: str = "en"):
        # 2. Build the Prompts
        system_instruction = get_risk_system_prompt()
        if lang == "it":
            system_instruction += "\n\nIMPORTANT: You MUST generate your ENTIRE response in fluent Italian."
        else:
            system_instruction += "\n\nIMPORTANT: You MUST generate your ENTIRE response in English."
            
        user_prompt = get_risk_user_prompt(question_text, json_payload)
        
        # 3. Stream the Groq/Gemini response
        for chunk in self.llm_client.stream_inference(system_instruction, user_prompt, question_id, lang):
            yield chunk

    def run_repair_quote_generation(self, json_payload: str, component_id: str, shop_name: str, driver_name: str, lang: str = "en"):
        # UI Loading Header
        if lang == "it":
            yield f"### 🛠️ Generazione Preventivo per {component_id}\nContattando **{shop_name}**...\n\n"
        else:
            yield f"### 🛠️ Generating Quote for {component_id}\nContacting **{shop_name}**...\n\n"
        
        time.sleep(0.5)
        system_instruction = get_repair_system_prompt()
        
        if lang == "it":
            system_instruction += "\n\nIMPORTANT: You MUST generate your ENTIRE response in fluent Italian."
        else:
            system_instruction += "\n\nIMPORTANT: You MUST generate your ENTIRE response in English."
            
        user_prompt = get_repair_user_prompt(json_payload, shop_name, driver_name)
        
        for chunk in self.llm_client.stream_inference(system_instruction, user_prompt, component_id, lang):
            yield chunk
