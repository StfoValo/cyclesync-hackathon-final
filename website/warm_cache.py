import requests
import time

# Replace with your actual Render URL
BASE_URL = "https://veritwin-digital-twin.onrender.com"

# ALL 20 Italian Regions from your Dashboard Dropdowns
TARGET_REGIONS = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
    "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche",
    "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia",
    "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"
]

# The languages supported by your i18n engine
LANGUAGES = ["en", "it"]

# The 6 Predefined Queries from the Executive Tab
PREDEFINED_QUERIES = [
    {"id": "exec_reg_1", "text": "Compare the average premium and risk distribution across regions."},
    {"id": "exec_reg_2", "text": "Which region shows the highest concentration of critical claims?"},
    {"id": "exec_demo_1", "text": "Analyze claim frequencies by driver age and gender."},
    {"id": "exec_demo_2", "text": "What is the correlation between vehicle category and behavioral risk?"},
    {"id": "exec_asset_1", "text": "Show me the component risk distribution across the fleet."},
    {"id": "exec_asset_2", "text": "Analyze the global VSI scores and project hardware failure costs."}
]

print(f"🚀 Starting VeriTwin Cloud Cache Pre-Warmer...")
total_calls = (len(TARGET_REGIONS) * len(LANGUAGES) * 2) + (len(PREDEFINED_QUERIES) * len(LANGUAGES))
print(f"📊 Total AI endpoints to warm up: {total_calls}\n")

# ==========================================
# PHASE 1: WARM UP GLOBAL EXECUTIVE QUERIES
# ==========================================
print("⏳ WARMING PHASE 1: Executive Risk Chat (Predefined Queries)...")
for lang in LANGUAGES:
    for query in PREDEFINED_QUERIES:
        print(f"   -> Hitting Risk Query: {query['id']} ({lang.upper()})")
        url = f"{BASE_URL}/api/ai/ask-predefined"
        payload = {
            "question_id": query['id'],
            "question_text": query['text'],
            "language": lang
        }
        try:
            # Note: This is a POST request!
            requests.post(url, json=payload, timeout=20)
            print("   ✅ Risk Query Warmed.")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        time.sleep(2) # Brief pause to respect rate limits

print("-" * 40)

# ==========================================
# PHASE 2: WARM UP REGIONAL ROUTING & ESG
# ==========================================
print("⏳ WARMING PHASE 2: Regional AI Routing & Circular Logistics...")
for region in TARGET_REGIONS:
    for lang in LANGUAGES:
        print(f"📍 Warming Region: {region} ({lang.upper()})...")
        
        # 1. Ping the AI Logistics Endpoint
        logistics_url = f"{BASE_URL}/api/ai/circular-logistics/{region}?lang={lang}"
        print(f"   -> Hitting: {logistics_url}")
        try:
            requests.get(logistics_url, timeout=20)
            print("   ✅ Logistics Warmed.")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            
        time.sleep(2) 
        
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

print("\n🎉 Pre-Warming Complete! The Executive Tab, AI Routing, and ESG engines are fully cached and pitch-ready!")

# ==========================================
# PHASE 3: WARM UP DRIVER APP REPAIR QUOTES
# ==========================================
print("⏳ WARMING PHASE 3: Driver App Repair Quotes...")

# The specific alerts we want to cache for the demo
DEMO_COMPONENTS = [
    {
        "component_id": "tire_RR",
        "issue_description": "Battistrada residuo: 2.1mm",
        "wear_level": "92.2",
        "shop_name": "Pneus Master",
        "driver_name": "Andrea"
    },
    {
        "component_id": "brake_pad_rear",
        "issue_description": "Sostituzione consigliata.",
        "wear_level": "84.0",
        "shop_name": "Pneus Master", 
        "driver_name": "Andrea"
    }
]

for lang in LANGUAGES:
    for comp in DEMO_COMPONENTS:
        print(f"   -> Hitting Repair Quote: {comp['component_id']} ({lang.upper()}) at {comp['shop_name']}")
        
        url = f"{BASE_URL}/api/ai/repair-quote"
        payload = {
            "component_id": comp["component_id"],
            "issue_description": comp["issue_description"],
            "wear_level": comp["wear_level"],
            "shop_name": comp["shop_name"],
            "driver_name": comp["driver_name"],
            "language": lang
        }
        
        try:
            requests.post(url, json=payload, timeout=20)
            print(f"   ✅ {comp['component_id']} Warmed.")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            
        time.sleep(2) # Brief pause to respect rate limits

print("-" * 40)