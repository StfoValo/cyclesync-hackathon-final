import os
import sys
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.gzip import GZipMiddleware

# Setup path for models
current_dir = os.path.dirname(os.path.abspath(__file__))
cycle_sync_app_dir = os.path.abspath(os.path.join(current_dir, "..", "cycle_sync_app"))
sys.path.insert(0, cycle_sync_app_dir)

# --- THE FIX: Tell Python to look inside the current 'website' folder for routers ---
sys.path.insert(0, current_dir)

from routers.insurer_api import router as insurer_router
from routers.ai_api import router as ai_router
# 1. ADD THIS IMPORT:
from routers.vehicle_api import router as vehicle_router
from models.data_manager.investigation_seeder import migrate_and_seed as _migrate_investigations
from models.data_manager.esg_seeder import migrate_and_seed as _migrate_esg
from models.data_manager.telemetry_seeder import migrate as _migrate_telemetry
from models.data_manager.fleet_demo_seeder import migrate_and_seed as _migrate_fleet_demo
from models.data_manager.incident_telemetry_seeder import migrate_and_seed as _migrate_incident_telemetry

app = FastAPI()

# ── Gzip compression for JSON/HTML payloads (minimum size 1 KB) ──────────
# Big wins: /api/db/vehicles (10 KB+), /api/db/components (40 KB+) shrink
# by ~70% over the wire so 50 concurrent fetchers don't saturate Render's
# free-tier egress.
app.add_middleware(GZipMiddleware, minimum_size=1024)


# ── HTTP cache headers on read-only DB endpoints ─────────────────────────
# Lets the browser (and any intermediate CDN) skip the round-trip for
# repeated GETs during a demo, which is critical when 50 viewers are all
# loading the dashboard at once.
#   • /api/db/*         → 60 s public cache (seed data is idempotent)
#   • /api/db/telemetry/categories → 5 min (almost immutable)
#   • /api/db/investigations/*/telemetry-samples → 5 min (locked window)
#   • /api/fleet/map    → already cached server-side; add browser cache too
@app.middleware("http")
async def _http_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.method != "GET":
        return response
    path = request.url.path
    if path.startswith("/api/db/telemetry/categories"):
        response.headers["Cache-Control"] = "public, max-age=300"
    elif "/telemetry-samples" in path or "/photos" in path:
        response.headers["Cache-Control"] = "public, max-age=300"
    elif path.startswith("/api/db/") or path.startswith("/api/driver/"):
        response.headers["Cache-Control"] = "public, max-age=60"
    elif path.startswith("/api/actuarial/"):
        response.headers["Cache-Control"] = "public, max-age=120"
    elif path.startswith("/storage/") or path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.on_event("startup")
def _bootstrap_adjuster_schema():
    """Ensure the Adjuster portal's columns + demo cases exist in cyclesync.db."""
    _migrate_investigations()

@app.on_event("startup")
def _bootstrap_telemetry_schema():
    """Extend vehicle_telemetry with blackbox + OBD-II + EV raw-signal columns."""
    _migrate_telemetry()

@app.on_event("startup")
def _bootstrap_fleet_demo():
    """Cull the fleet to 10 hand-tuned vehicles + populate realistic telemetry.

    Runs AFTER the telemetry / investigation seeders so all columns and FK
    targets exist. Idempotent via the `fleet_demo_v1` marker — drop the row
    from `_seeder_state` to force a re-run.
    """
    _migrate_fleet_demo()

@app.on_event("startup")
def _bootstrap_esg_schema():
    """Ensure the ESG inventory columns + telemetry-driven component seed.

    Runs AFTER fleet_demo so the seeder operates on the 10 surviving vehicles
    (and their live telemetry counters) rather than the 3 000-vehicle raw set.
    """
    _migrate_esg()

@app.on_event("startup")
def _bootstrap_incident_telemetry():
    """Seed ±5 min telemetry samples around each investigation's impact moment."""
    _migrate_incident_telemetry()

app.include_router(insurer_router)
app.include_router(ai_router)
# 2. ADD THIS INCLUSION:
app.include_router(vehicle_router)

static_dir = os.path.join(current_dir, "static")
os.makedirs(static_dir, exist_ok=True)

# THE FIX: Mount the parent storage folder for ultra-fast direct media access
storage_dir = os.path.abspath(os.path.join(current_dir, "..", "storage"))
app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")

# --- Clean Frontpage Routing ---
@app.get("/")
def read_root():
    """Serves the new Digital Twin landing page."""
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/dashboard")
def read_dashboard():
    """Serves the enterprise dashboard."""
    return FileResponse(os.path.join(static_dir, "dashboard.html"))

@app.get("/driver")
def read_driver_app():
    """Serves the consumer-facing mobile web app."""
    return FileResponse(os.path.join(static_dir, "user_app.html"))

# Mount static files for JS, CSS, and Images
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.head("/")
async def ping_head():
    """
    Intercepts UptimeRobot's HEAD requests and returns a 200 OK 
    so it stops logging 405 Method Not Allowed errors.
    """
    return {"status": "VeriTwin is awake!"}