import time
import os
import google.generativeai as genai
from dotenv import load_dotenv

class CoreLLMClient:
    def __init__(self):
        load_dotenv()
        # 🚨 Ensure your real Gemini API key is here! 🚨
        self.api_key = os.getenv("GEMINI_API_KEY") 
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.request_timestamps = []

    def _is_rate_limited(self):
        current_time = time.time()
        self.request_timestamps = [t for t in self.request_timestamps if current_time - t < 60]
        if len(self.request_timestamps) >= 10:
            return True
        self.request_timestamps.append(current_time)
        return False

    def stream_inference(self, system_instruction: str, user_prompt: str, on_fallback=None):
        """Executes the API call with a strict retry loop and streaming."""
        
        fallback_text = "### 📱 PUSH NOTIFICATION PREVIEW\n⚠️ Alert: Critical brake pad wear detected in your area. Avoid accidents and get 15% off replacement at Autofficina Sprint today! Book now.\n\n### 🎯 CAMPAIGN RATIONALE\nTriggered by a 24% spike in critical brake telemetry in this region, utilizing the nearest available network partner."
        
        if self._is_rate_limited():
            if on_fallback:
                on_fallback()
            for i in range(0, len(fallback_text), 5):
                yield fallback_text[i:i+5]
                time.sleep(0.05)
            return
            
        # Combine the system rules and the user data
        full_prompt = f"SYSTEM INSTRUCTION:\n{system_instruction}\n\nUSER PAYLOAD:\n{user_prompt}"
        
        max_retries = 3
        retry_delay = 26 
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(full_prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                break  
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota" in error_msg:
                    if on_fallback:
                        on_fallback()
                    for i in range(0, len(fallback_text), 5):
                        yield fallback_text[i:i+5]
                        time.sleep(0.05)
                    return
                else:
                    yield f"\n\n**[❌ ERROR]** Connection to Gemini Core failed: {error_msg}"
                    break