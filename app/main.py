from fastapi import FastAPI
from app.api.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Wine Intelligence Analyzer",
    version="1.0",
    description="App to analyze wine with WSET SAT (Systematic Approach to Tasting)",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS to allow request from any frontend (can be locked down later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix="/api")

# Health check or demo route
@app.get("/")
def read_root():
    return {"message": "Wine Analyzer API is running"}