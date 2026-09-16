from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routers.hotspots import router as hotspots_router
from src.api.routers.prediction import router as prediction_router

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
INDEX_HTML = FRONTEND_DIST / "index.html"

app = FastAPI(
    title="SIH26162 — Thermal Intelligence & Early Warning System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount compiled React Vite assets if dist exists
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "system": "SIH26162 Thermal Intelligence",
        "version": "1.0.0"
    }

@app.get("/dashboard", response_class=FileResponse)
@app.get("/", response_class=FileResponse)
def serve_dashboard():
    if INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    return {"message": "React Vite frontend dist build not found. Run npm run build in frontend/"}

app.include_router(hotspots_router)
app.include_router(prediction_router)