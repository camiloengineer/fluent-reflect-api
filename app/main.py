from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.execute import router as execute_router
from app.routes.chat import router as chat_router
from app.routes.challenge import router as challenge_router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Fluent Reflect API",
    description="Backend for code execution, AI chat, and challenge generation using Judge0 and OpenAI APIs",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(execute_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(challenge_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Fluent Reflect API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)