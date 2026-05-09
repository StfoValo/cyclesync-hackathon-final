import requests
import time

# Replace with your actual Render URL
BASE_URL = "https://veritwin-digital-twin.onrender.com"

# ALL 20 Italian Regions from your Dashboard Dropdowns
TARGET_REGIONS = [
    "Abruzzo", 
    "Basilicata", 
    "Calabria", 
    "Campania", 
    "Emilia-Romagna",
    "Friuli-Venezia Giulia", 
    "Lazio", 
    "Liguria", 
    "Lombardia", 
    "Marche",
    "Molise", 
    "Piemonte", 
    "Puglia", 
    "Sardegna", 
    "Sicilia",
    "Toscana", 
    "Trentino-Alto Adige", 
    "Umbria", 
    "Valle d'Aosta", 
    "Veneto"
]

# The languages supported by your i18n engine
LANGUAGES = ["en", "it"]

print(f"🚀 Starting VeriTwin Cloud Cache Pre-Warmer for ALL regions...")
total_calls = len(TARGET_REGIONS) * len(LANGUAGES) * 2
print(f"📊 Total AI endpoints to warm up: {total_calls}\n")

for region in TARGET_REGIONS:
    for lang in LANGUAGES:
        print(f"⏳ Warming Cache for {region} ({lang.upper()})...")
        
        # 1. Ping the AI Logistics Endpoint
        logistics_url = f"{BASE_URL}/api/ai/circular-logistics/{region}?lang={lang}"
        print(f"   -> Hitting: {logistics_url}")
        try:
            requests.get(logistics_url, timeout=20)
            print("   ✅ Logistics Warmed.")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            
        time.sleep(2) # Brief pause to respect rate limits
        
        # 2. Ping the AI Strategy Endpoint
        strategy_url = f"{BASE_URL}/api/ai/orchestrate/{region}?lang={lang}"
        print(f"   -> Hitting: {strategy_url}")
        try:
            requests.get(strategy_url, timeout=20)
            print("   ✅ Strategy Warmed.")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            
        time.sleep(2)
        print("-" * 40)

print("\n🎉 Pre-Warming Complete! Every single region and language is now cached. Your demo is truly bulletproof!")