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
        """Three-tier LLM router optimised for concurrent demo traffic.

        Tier 1 (NEW — Shadow Cache, ~0 ms / no API quota)
            Returns the last-known-good response from the in-RAM fallback
            JSON. Hit by every warm-cache combo (region × lang × prompt
            type). This is what makes 50 simultaneous viewers feasible
            on a Render free worker: no AI call is made during the demo
            unless someone hits an UNWARMED combination.

        Tier 2 — Groq (fast, ~1-3 s)
            For novel inputs (or a cold cache after redeploy). Result is
            persisted into the shadow cache so subsequent identical
            requests serve from RAM.

        Tier 3 — Gemini (~3-8 s)
            Last AI resort if Groq is down / over quota.

        Tier 4 — Friendly offline message
            Engaged only if all three above fail.
        """
        language_command = "Italian" if lang == "it" else "English"
        system_instruction += f"\n\nCRITICAL INSTRUCTION: You MUST generate your entire response in {language_command}."

        # The key becomes "tire_RR_it" or "brake_pad_rear_en"
        cache_key = f"{region}_{lang}"
        full_prompt = f"SYSTEM INSTRUCTION:\n{system_instruction}\n\nUSER PAYLOAD:\n{user_prompt}"
        prompt_type = "logistics" if "Reverse Logistics" in system_instruction else \
                      "repair"    if "Service Agent"      in system_instruction else \
                      "campaign"

        # ── TIER 1: Shadow cache (RAM-resident, instant) ─────────────────
        self._load_cache_to_memory()
        cached = (self._memory_cache.get(prompt_type, {}) or {}).get(cache_key)
        if cached:
            print(f"[LLM Router] 💨 TIER 1 HIT — shadow cache for {cache_key} ({prompt_type}). Streaming locally.")
            # Replay the cached response in chunks so the UI keeps its
            # typewriter feel. ~30 ms per word keeps the stream alive but
            # finishes a typical 300-word response in ~9 s — already 2-3×
            # faster than a live Groq round-trip and uses zero quota.
            for word in cached.split(" "):
                yield word + " "
                time.sleep(0.02)
            return

        # ── TIER 2: Groq (fast LLM) ──────────────────────────────────────
        if self.groq_client:
            try:
                print(f"[LLM Router] Attempting Tier 2: Groq for {cache_key} (8.0 s timeout)…")
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=True,
                    timeout=8.0,
                )

                full_text_accumulator = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_text_accumulator += content
                        yield content

                self._save_regional_fallback(prompt_type, cache_key, full_text_accumulator)
                return

            except Exception as e:
                print(f"[LLM Router] ⚠️ Groq failed: {e}")

        # ── TIER 3: Gemini ───────────────────────────────────────────────
        try:
            print(f"[LLM Router] Attempting Tier 3: Gemini for {cache_key} (10.0 s timeout)…")
            response = self.gemini_model.generate_content(
                full_prompt, stream=True, request_options={"timeout": 10.0},
            )

            full_text_accumulator = ""
            for chunk in response:
                if chunk.text:
                    full_text_accumulator += chunk.text
                    yield chunk.text

            self._save_regional_fallback(prompt_type, cache_key, full_text_accumulator)
            return

        except Exception as e:
            print(f"[LLM Router] ⚠️ Gemini failed: {e}")

        # ── TIER 4: Friendly offline fallback ────────────────────────────
        print(f"[LLM Router] 🛑 All tiers exhausted for {cache_key}.")
        offline_msg = self._get_regional_fallback(prompt_type, cache_key)
        for word in offline_msg.split(" "):
            yield word + " "
            time.sleep(0.04)

    # ---------------------------------------------------------
    # DYNAMIC CACHE MANAGER LOGIC (IN-MEMORY RAM OPTIMIZED)
    # ---------------------------------------------------------
    def _load_cache_to_memory(self):
        """Loads the JSON into RAM exactly once to prevent Disk I/O bottlenecks."""
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
            if prompt_type not in self._memory_cache:
                self._memory_cache[prompt_type] = {}
                
            # Bypass disk write if it already exists
            if region in self._memory_cache[prompt_type]:
                print(f"[Shadow Cache] ⏭️ Cache already exists for {region} ({prompt_type}). Skipping disk write.")
                return 
                
            self._memory_cache[prompt_type][region] = response_text
            
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
            
            if region in category:
                return category[region]
            elif "default" in category:
                return category["default"]
                
            return "### ⚠️ OFFLINE\nImpossibile generare il preventivo al momento." if "_it" in region else "### ⚠️ OFFLINE\nCould not generate quote at this time."
        except Exception as e:
            return f"### ⚠️ CACHE ERROR\n{str(e)}"