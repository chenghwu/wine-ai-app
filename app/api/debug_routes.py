import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/env", summary="Show selected environment variables (dev only)")
async def debug_env():
    keys_to_check = [
        "ENV",
        "USE_MOCK",
        "ALLOWED_ORIGINS",
        "DB_HOST",
        "LAST_UPDATED"
    ]
    return {key: os.getenv(key, "[NOT SET]") for key in keys_to_check}