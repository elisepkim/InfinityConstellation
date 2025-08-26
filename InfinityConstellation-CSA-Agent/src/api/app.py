from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import router as api_router

app = FastAPI(title="Infinity CSA Data Intelligence API (MassGen)")

# CORS - allow all origins for demo (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def health():
    return {"status": "ok", "service": "infinity-csa-api"}