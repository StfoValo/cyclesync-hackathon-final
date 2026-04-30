import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse # <--- NEW IMPORT

# Setup path for models
current_dir = os.path.dirname(os.path.abspath(__file__))
cycle_sync_app_dir = os.path.abspath(os.path.join(current_dir, "..", "cycle_sync_app"))
sys.path.insert(0, cycle_sync_app_dir)

from routers.insurer_api import router as insurer_router
from routers.ai_api import router as ai_router

app = FastAPI()

app.include_router(insurer_router)
app.include_router(ai_router)

# --- NEW: Automatically redirect the root URL to the dashboard ---
@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

static_dir = os.path.join(current_dir, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
