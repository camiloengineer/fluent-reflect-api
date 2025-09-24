from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.execute import router as execute_router
from app.routes.chat import router as chat_router
from app.routes.challenge import router as challenge_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Fluent Reflect API",
    description="Backend for code execution, AI chat, and challenge generation using Judge0 and OpenAI APIs",
    version="1.0.0"
)

# CORS middleware for frontend integration
ALLOWED_ORIGINS = [
    "https://fluent-reflect-app.web.app",
    "https://fluent-reflect-front-d5vnsr2t6q-uc.a.run.app",  # Frontend production
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

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