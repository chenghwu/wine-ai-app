from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="Wine Analyzer",
    version="0.1.0",
    description="App to analyze wine with WSET SAT (Systematic Approach to Tasting)",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(api_router, prefix="/api")