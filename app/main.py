from fastapi import FastAPI
from app.api.routes import router as api_router
from app.utils import env
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

app = FastAPI(
    title="Wine Intelligence Analyzer",
    version="1.0",
    description="App to analyze wine with WSET SAT (Systematic Approach to Tasting)",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Parse comma-separated CORS origins
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
origins = [o.strip() for o in origins if o.strip()]

# Enable CORS to allow request from any frontend (can be locked down later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # only allow listed origins
    allow_credentials=True,
    allow_methods=["*"],    # allow all HTTP methods
    allow_headers=["*"]     # allow all headers
)

# Routes
app.include_router(api_router, prefix="/api")

# Conditionally include debug routes for dev mode
if os.getenv("ENV") == "dev":
    from app.api.debug_routes import router as debug_router
    app.include_router(debug_router, prefix="/debug")

# Health check or demo route
@app.get("/")
def read_root():
    return {"message": "Wine Analyzer API is running"}