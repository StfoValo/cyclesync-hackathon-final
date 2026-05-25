import requests
import time
import sys

# Change port if your FastAPI runs on a different one
URL = "https://cyclesync-digital-twin-keyo.onrender.com//api/ai/repair-quote"

PAYLOAD = {
    "component_id": "tire_RR",
    "issue_description": "Battistrada residuo: 2.1mm",
    "wear_level": "92.2",
    "shop_name": "Pneus Master",
    "driver_name": "Andrea",
    "language": "it"
}

def simulate_request(attempt_name):
    print(f"\n{'='*40}")
    print(f"🚀 RUNNING: {attempt_name}")
    print(f"{'='*40}")
    
    start_time = time.time()
    
    try:
        # We use stream=True because it is a StreamingResponse
        with requests.post(URL, json=PAYLOAD, stream=True, timeout=15) as response:
            print("🤖 Streaming Output:\n")
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
        
        elapsed = time.time() - start_time
        print(f"\n\n⏱️ Total Time: {elapsed:.2f} seconds")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Connection Error: Make sure the FastAPI server is running! ({e})")

if __name__ == "__main__":
    print("🧪 INITIALIZING CACHE PIPELINE TEST...")
    
    # 1. First run populates the cache
    simulate_request("Attempt 1 (Populating Cache)")
    
    print("\n⏳ Waiting 3 seconds...")
    time.sleep(3)
    
    # 2. Second run verifies the RAM Write-Lock bypass
    simulate_request("Attempt 2 (Verifying RAM Write-Lock)")
    
    print("\n✅ TEST SCRIPT COMPLETE.")
    print("To test the ACTUAL fallback, turn off your WiFi and run this script again!")