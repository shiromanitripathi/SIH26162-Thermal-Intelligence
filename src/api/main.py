from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.hotspots import router as hotspots_router
from src.api.routers.prediction import router as prediction_router


app = FastAPI(
    title="Thermal Intelligence & Early Warning System",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok"
    }


app.include_router(hotspots_router)
app.include_router(prediction_router)