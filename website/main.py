import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse 

# Setup path for models
current_dir = os.path.dirname(os.path.abspath(__file__))
cycle_sync_app_dir = os.path.abspath(os.path.join(current_dir, "..", "cycle_sync_app"))
sys.path.insert(0, cycle_sync_app_dir)

# --- THE FIX: Tell Python to look inside the current 'website' folder for routers ---
sys.path.insert(0, current_dir)

from routers.insurer_api import router as insurer_router
from routers.ai_api import router as ai_router

app = FastAPI()

app.include_router(insurer_router)
app.include_router(ai_router)

static_dir = os.path.join(current_dir, "static")
os.makedirs(static_dir, exist_ok=True)

# --- NEW: Clean Frontpage Routing ---
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

@app.get("/driver")
def read_driver_app():
    """Serves the consumer-facing mobile web app."""
    return FileResponse(os.path.join(static_dir, "user_app.html"))

@app.head("/")
async def ping_head():
    """
    Intercepts UptimeRobot's HEAD requests and returns a 200 OK 
    so it stops logging 405 Method Not Allowed errors.
    """
    return {"status": "VeriTwin is awake!"}