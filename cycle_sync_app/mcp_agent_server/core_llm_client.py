import time
import os
import json
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

class CoreLLMClient:
    def __init__(self):
        load_dotenv()
        
        # --- TIER 1: Gemini Setup ---
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") 
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')

        # --- TIER 2: Groq Setup ---
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None

        # Path to our Shadow Cache file
        self.cache_file_path = os.path.join(os.path.dirname(__file__), "fallback_responses.json")

    def stream_inference(self, system_instruction: str, user_prompt: str, region: str = "default", lang: str = "en"):
        # --- FIX 1: Enforce the language instruction directly on the LLM System Prompt ---
        language_command = "Italian" if lang == "it" else "English"
        system_instruction += f"\n\nCRITICAL INSTRUCTION: You MUST generate your entire response in {language_command}."
        
        # --- FIX 2: Make the Cache key language-aware (e.g., Abruzzo_it) ---
        cache_key = f"{region}_{lang}"
        
        full_prompt = f"SYSTEM INSTRUCTION:\n{system_instruction}\n\nUSER PAYLOAD:\n{user_prompt}"
        # Update this line to include the repair prompt type
        prompt_type = "logistics" if "Reverse Logistics" in system_instruction else "repair" if "Service Agent" in system_instruction else "campaign"

        if self.groq_client:
            try:
                print(f"[LLM Router] Attempting Tier 1: Groq Fallback for {region} ({lang}) (8.0s timeout)...")
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True,
                    timeout=8.0 
                )
                
                full_text_accumulator = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_text_accumulator += content
                        yield content
                
                # Save using the language-aware cache key
                self._save_regional_fallback(prompt_type, cache_key, full_text_accumulator)
                return 
                
            except Exception as e:
                print(f"[LLM Router] ⚠️ Groq failed: {str(e)}")
        
        try:
            print(f"[LLM Router] Attempting Tier 2: Gemini for {region} ({lang}) (10.0s timeout)...")
            response = self.gemini_model.generate_content(
                full_prompt, stream=True, request_options={"timeout": 10.0} 
            )
            
            full_text_accumulator = ""
            for chunk in response:
                if chunk.text:
                    full_text_accumulator += chunk.text
                    yield chunk.text
            
            # Save using the language-aware cache key
            self._save_regional_fallback(prompt_type, cache_key, full_text_accumulator)
            return 
            
        except Exception as e:
            print(f"[LLM Router] ⚠️ Gemini failed: {str(e)}")

        print(f"[LLM Router] 🛑 Engaging Tier 3 Local Cache for {cache_key}...")
        time.sleep(0.8) 
        
        # Retrieve using the language-aware cache key
        cached_response = self._get_regional_fallback(prompt_type, cache_key)
            
        words = cached_response.split(" ")
        for word in words:
            yield word + " "
            time.sleep(0.04)

    # ---------------------------------------------------------
    # DYNAMIC CACHE MANAGER LOGIC (IN-MEMORY RAM OPTIMIZED)
    # ---------------------------------------------------------
    def _load_cache_to_memory(self):
        """Loads the JSON into RAM exactly once to prevent Disk I/O bottlenecks."""
        # Only read from the disk if the memory cache doesn't exist yet
        if not hasattr(self, '_memory_cache') or self._memory_cache is None:
            try:
                if os.path.exists(self.cache_file_path):
                    with open(self.cache_file_path, "r", encoding="utf-8") as f:
                        self._memory_cache = json.load(f)
                    print("[Shadow Cache] 🚀 Loaded fallback JSON into RAM.")
                else:
                    self._memory_cache = {"logistics": {}, "campaign": {}, "repair": {}}
            except Exception as e:
                print(f"[Shadow Cache] ⚠️ Error loading to memory: {e}")
                self._memory_cache = {"logistics": {}, "campaign": {}, "repair": {}}

    def _save_regional_fallback(self, prompt_type: str, region: str, response_text: str):
        """Silently saves successful LLM generations to RAM and syncs to disk ONLY if new."""
        self._load_cache_to_memory()
        
        try:
            # Ensure the structure exists
            if prompt_type not in self._memory_cache:
                self._memory_cache[prompt_type] = {}
                
            # --- THE WRITE-LOCK BYPASS (Checked instantly via RAM) ---
            if region in self._memory_cache[prompt_type]:
                print(f"[Shadow Cache] ⏭️ Cache already exists for {region} ({prompt_type}). Skipping disk write.")
                return 
                
            # 1. Save to lightning-fast RAM memory for immediate use
            self._memory_cache[prompt_type][region] = response_text
            
            # 2. Persist to disk as a backup for the next server restart
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                json.dump(self._memory_cache, f, indent=4)
            print(f"[Shadow Cache] ✅ Successfully saved new fallback response to Disk/RAM for {region} ({prompt_type}).")
            
        except Exception as e:
            print(f"[Shadow Cache Error] Could not save to JSON: {e}")

    def _get_regional_fallback(self, prompt_type: str, region: str) -> str:
        """Reads the perfectly formatted regional response instantly from RAM (Zero Disk I/O)."""
        try:
            self._load_cache_to_memory()
            category = self._memory_cache.get(prompt_type, {})
            
            # Try to get exact region, if not, try to get a "default" one
            if region in category:
                return category[region]
            elif "default" in category:
                return category["default"]
                
            return "### ⚠️ SYSTEM OFFLINE\nCould not connect to AI services or retrieve local regional cache."
        except Exception as e:
            return f"### ⚠️ CACHE ERROR\n{str(e)}"