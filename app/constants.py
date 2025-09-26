import os
from typing import List

def get_allowed_origins() -> List[str]:
    """Get CORS allowed origins from environment variables"""
    return os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []

ALLOWED_ORIGINS = get_allowed_origins()