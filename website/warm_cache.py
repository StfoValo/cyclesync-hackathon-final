"""
VeriTwin × CycleSync — Cloud Cache Pre-Warmer.

Run this AFTER every fresh Render deploy and BEFORE the demo. Each hit
populates the in-RAM shadow cache (fallback_responses.json) for the AI
endpoints, so during the live demo every subsequent identical request
serves instantly from RAM with zero Groq/Gemini quota cost.

Tiers hit (in order):
    1. Predefined Executive Risk Chat queries  (6 × 2 langs = 12)
    2. AI Routing per region                   (20 × 2 langs = 40)
    3. ESG Reverse Logistics per region         (20 × 2 langs = 40)
    4. ESG Batch Recycling per category         (9 × 2 langs = 18)
    5. Adjuster investigation AI                (5 × 2 langs = 10)
    6. Driver SOS per linked VIN                (2 × 2 langs = 4)
    7. Driver Repair Quote per (component, shop) (8 × 2 langs = 16)

Total target: 140 cache fills (≈ 25 minutes with conservative pacing).

Usage:
    python website/warm_cache.py
    python website/warm_cache.py --base http://localhost:8001    # local
    python website/warm_cache.py --quick                         # essentials only
"""
import argparse
import time
import requests


# ──────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────
DEFAULT_BASE_URL = "https://cyclesync-veritwin.onrender.com"
LANGUAGES = ["en", "it"]

TARGET_REGIONS = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
    "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche",
    "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia",
    "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto",
]

PREDEFINED_QUERIES = [
    {"id": "exec_reg_1",   "text": "Compare the average premium and risk distribution across regions."},
    {"id": "exec_reg_2",   "text": "Which region shows the highest concentration of critical claims?"},
    {"id": "exec_demo_1",  "text": "Analyze claim frequencies by driver age and gender."},
    {"id": "exec_demo_2",  "text": "What is the correlation between vehicle category and behavioral risk?"},
    {"id": "exec_asset_1", "text": "Show me the component risk distribution across the fleet."},
    {"id": "exec_asset_2", "text": "Analyze the global VSI scores and project hardware failure costs."},
]

# All 8 ESG component categories + "all" (which is what the dropdown opens with).
BATCH_CATEGORIES = [
    "all", "tire", "brake_pad", "brake_disc", "suspension_damper",
    "aux_12v_battery", "engine_oil", "dpf", "ev_battery",
]

# The 5 demo investigation cases (set by investigation_seeder.py).
INVESTIGATIONS = [
    "CASE-2024-00142",   # Maserati red-light runner (4.2 g, fraud risk 72%)
    "CASE-2024-00287",   # Tesla rear-end (1.8 g, fraud risk 15%)
    "CASE-2024-00391",   # Fiat 500e tractor impact (6.1 g)
    "CASE-2025-00012",   # VW Golf T-junction (3.0 g lateral)
    "CASE-2025-00045",   # BMW X5 head-on (5.5 g)
]

# Andrea's two linked vehicles (driver_id=1 garage).
DRIVER_VINS = [
    "SIMD9486C283C8C4D",   # Maserati Grecale Folgore (pinned)
    "SIM00E85293920545",   # Tesla Model 3
]

# Components the Adjuster / Driver app surfaces "Get Repair Quote" CTA for.
DEMO_REPAIR_COMPONENTS = [
    {"component_id": "tire_RR",       "issue_description": "Battistrada residuo: 2.1mm",
     "wear_level": "92.2", "shop_name": "Pneus Master"},
    {"component_id": "tire_FL",       "issue_description": "Battistrada residuo: 2.4mm",
     "wear_level": "88.0", "shop_name": "Pneus Master"},
    {"component_id": "brake_pad_front","issue_description": "Sostituzione consigliata.",
     "wear_level": "82.8", "shop_name": "Officina Antonelli"},
    {"component_id": "brake_pad_rear", "issue_description": "Sostituzione consigliata.",
     "wear_level": "84.0", "shop_name": "Officina Antonelli"},
    {"component_id": "aux_12v_battery_main", "issue_description": "Failed cranking-voltage test",
     "wear_level": "78.0", "shop_name": "Officina Antonelli"},
    {"component_id": "engine_oil_main",  "issue_description": "Olio motore esausto",
     "wear_level": "85.0", "shop_name": "Officina Antonelli"},
    {"component_id": "dpf_main",         "issue_description": "DPF saturo",
     "wear_level": "90.0", "shop_name": "Officina Antonelli"},
    {"component_id": "ev_battery_main",  "issue_description": "SOH ridotto",
     "wear_level": "22.0", "shop_name": "Pneus Master"},
]

DRIVER_NAME = "Andrea"


# ──────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────
def _hit(method: str, url: str, *, json_body=None, timeout=30, label=""):
    """Fire one request, draining the streaming body so the server fully
    completes generation (and thus persists to the shadow cache)."""
    try:
        if method == "GET":
            r = requests.get(url, timeout=timeout, stream=True)
        else:
            r = requests.post(url, json=json_body, timeout=timeout, stream=True)
        # Drain the stream — important for streaming endpoints.
        for _ in r.iter_content(chunk_size=4096):
            pass
        ok = "✅" if r.status_code == 200 else f"⚠️  {r.status_code}"
        print(f"   {ok} {label or url}")
    except Exception as e:
        print(f"   ⚠️  ERROR {label or url} — {e}")


def _phase(title: str):
    print()
    print("─" * 60)
    print(f"⏳  {title}")
    print("─" * 60)


# ──────────────────────────────────────────────────────────────────────────
# WARM-UP PHASES
# ──────────────────────────────────────────────────────────────────────────
def warm_executive(base_url: str, langs):
    _phase("Phase 1: Executive Risk Chat — predefined queries")
    for lang in langs:
        for q in PREDEFINED_QUERIES:
            _hit("POST", f"{base_url}/api/ai/ask-predefined",
                 json_body={"question_id": q["id"], "question_text": q["text"], "language": lang},
                 label=f"{q['id']} ({lang})")
            time.sleep(1.5)


def warm_ai_routing(base_url: str, regions, langs):
    _phase("Phase 2: AI Routing — strategy per region × lang")
    for region in regions:
        for lang in langs:
            _hit("GET",
                 f"{base_url}/api/ai/orchestrate/{requests.utils.quote(region)}?lang={lang}",
                 label=f"orchestrate {region} ({lang})")
            time.sleep(1.5)


def warm_esg_logistics(base_url: str, regions, langs):
    _phase("Phase 3: ESG Reverse Logistics — per region × lang")
    for region in regions:
        for lang in langs:
            _hit("GET",
                 f"{base_url}/api/ai/circular-logistics/{requests.utils.quote(region)}?lang={lang}",
                 label=f"logistics {region} ({lang})")
            time.sleep(1.5)


def warm_batch_recycling(base_url: str, langs):
    _phase("Phase 4: ESG Batch Recycling — per category × lang")
    for cat in BATCH_CATEGORIES:
        for lang in langs:
            _hit("GET",
                 f"{base_url}/api/ai/batch-recycling/{cat}?lang={lang}",
                 label=f"batch {cat} ({lang})")
            time.sleep(1.5)


def warm_investigations(base_url: str, langs):
    _phase("Phase 5: Adjuster AI Fraud Analysis — per case × lang")
    for case in INVESTIGATIONS:
        for lang in langs:
            _hit("GET",
                 f"{base_url}/api/ai/investigation/{case}?lang={lang}",
                 label=f"investigation {case} ({lang})",
                 timeout=45)
            time.sleep(2.0)


def warm_driver_sos(base_url: str, langs):
    _phase("Phase 6: Driver SOS — per VIN × lang")
    for vin in DRIVER_VINS:
        for lang in langs:
            _hit("GET",
                 f"{base_url}/api/ai/sos/{vin}?lang={lang}",
                 label=f"SOS {vin[-6:]} ({lang})")
            time.sleep(1.5)


def warm_repair_quotes(base_url: str, langs):
    _phase("Phase 7: Driver Repair Quotes — per component × lang")
    for lang in langs:
        for comp in DEMO_REPAIR_COMPONENTS:
            body = {**comp, "driver_name": DRIVER_NAME, "language": lang}
            _hit("POST", f"{base_url}/api/ai/repair-quote", json_body=body,
                 label=f"quote {comp['component_id']} @ {comp['shop_name']} ({lang})")
            time.sleep(1.5)


# ──────────────────────────────────────────────────────────────────────────
# DB warm-up — touch the high-traffic read endpoints so the Python
# process has them in OS page cache.
# ──────────────────────────────────────────────────────────────────────────
def warm_db(base_url: str):
    _phase("Phase 0: Read-only DB endpoints (page-cache prime)")
    endpoints = [
        "/", "/dashboard", "/driver",
        "/api/db/vehicles?per_page=20",
        "/api/db/components/stats",
        "/api/db/components?per_page=20",
        "/api/db/investigations",
        "/api/db/telemetry/categories",
        "/api/driver/1",
        "/api/driver/vehicle/SIMD9486C283C8C4D/component-life",
        "/api/driver/vehicle/SIM00E85293920545/component-life",
        "/api/db/investigations/CASE-2024-00142",
        "/api/db/investigations/CASE-2024-00142/telemetry-samples",
        "/api/db/investigations/CASE-2024-00142/photos",
        "/api/db/investigations/CASE-2024-00287",
        "/api/db/investigations/CASE-2024-00391",
        "/api/db/investigations/CASE-2025-00012",
        "/api/db/investigations/CASE-2025-00045",
        "/api/actuarial/summary",
        "/api/actuarial/deep-dive",
        "/api/actuarial/esg",
        "/api/fleet/map?view=fleet&lang=en",
        "/api/fleet/map?view=fleet&lang=it",
        "/api/fleet/map?view=suppliers&lang=en",
        "/api/fleet/map?view=suppliers&lang=it",
    ]
    for ep in endpoints:
        _hit("GET", f"{base_url}{ep}", label=ep, timeout=20)
        time.sleep(0.3)


# ──────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Warm the AI shadow cache before the demo.")
    parser.add_argument("--base", default=DEFAULT_BASE_URL, help="Base URL of the deployed instance.")
    parser.add_argument("--quick", action="store_true",
                        help="Skip the heavy investigation + per-region passes.")
    parser.add_argument("--phase", type=int, default=None, choices=range(0, 8),
                        help="Run only the given phase number (0-7).")
    args = parser.parse_args()

    print(f"🚀 VeriTwin Cloud Cache Pre-Warmer")
    print(f"   Target: {args.base}")
    print(f"   Mode:   {'QUICK' if args.quick else 'FULL'}{f' phase={args.phase}' if args.phase is not None else ''}")

    phases = {
        0: lambda: warm_db(args.base),
        1: lambda: warm_executive(args.base, LANGUAGES),
        2: lambda: warm_ai_routing(args.base, TARGET_REGIONS if not args.quick else ["Lazio", "Lombardia"], LANGUAGES),
        3: lambda: warm_esg_logistics(args.base, TARGET_REGIONS if not args.quick else ["Lazio", "Lombardia"], LANGUAGES),
        4: lambda: warm_batch_recycling(args.base, LANGUAGES),
        5: lambda: warm_investigations(args.base, LANGUAGES),
        6: lambda: warm_driver_sos(args.base, LANGUAGES),
        7: lambda: warm_repair_quotes(args.base, LANGUAGES),
    }

    if args.phase is not None:
        phases[args.phase]()
    else:
        for n in sorted(phases.keys()):
            phases[n]()

    print()
    print("🎉  Pre-warming complete!")
    print("    From now on every cached endpoint serves from shadow cache in <100 ms.")
    print("    Re-run after any redeploy (Render wipes the JSON on cold start).")


if __name__ == "__main__":
    main()
