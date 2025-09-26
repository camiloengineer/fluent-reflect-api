from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes.execute import router as execute_router
from app.routes.chat import router as chat_router
from app.routes.challenge import router as challenge_router
from app.constants import ALLOWED_ORIGINS
from dotenv import load_dotenv
import httpx
import time
import os

load_dotenv()

ALLOW_COUNTRY = "CL"
ALLOW_CITY = "santiago"
CACHE_TTL = 600
FAIL_OPEN = False
GEO_API_URL = os.getenv("GEO_API_URL", "http://ip-api.com/json")

_cache = {}

def client_ip(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return req.client.host

async def geo(ip: str) -> dict:
    now = time.time()
    hit = _cache.get(ip)
    if hit and hit[0] > now:
        return hit[1]

    async with httpx.AsyncClient(timeout=1.5) as c:
        r = await c.get(f"{GEO_API_URL}/{ip}")
        r.raise_for_status()
        j = r.json()
        info = {
            "country": (j.get("countryCode") or "").upper(),
            "city": (j.get("city") or ""),
        }
        _cache[ip] = (now + CACHE_TTL, info)
        return info

app = FastAPI(
    title="Fluent Reflect API",
    description="Backend for code execution, AI chat, and challenge generation using Judge0 and OpenAI APIs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRFToken",
    ],
)

@app.middleware("http")
async def only_santiago(request: Request, call_next):
    if request.url.path in ("/health", "/metrics", "/"):
        return await call_next(request)

    ip = client_ip(request)
    try:
        g = await geo(ip)
        ok = (g["country"] == ALLOW_COUNTRY) and (ALLOW_CITY in g["city"].lower())
        if not ok:
            raise HTTPException(status_code=403, detail="Forbidden")
        return await call_next(request)
    except Exception:
        if FAIL_OPEN:
            return await call_next(request)
        raise HTTPException(status_code=403, detail="Forbidden")

# Include routes
app.include_router(execute_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(challenge_router, prefix="/api")

# Explicit OPTIONS handler for CORS preflight requests (after routers)
@app.options("/{path:path}")
async def options_handler():
    """Handle CORS preflight requests explicitly"""
    return {}

@app.get("/")
async def root():
    return {"message": "Fluent Reflect API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)