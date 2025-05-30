import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.helper.redis_helper import redis_manager
from app.services.chat_service import get_suggestion_places_from_db
from app.settings import (
    ALLOW_ALL_ORIGINS,
    CORS_ORIGINS,
    ENVIRONMENT,
    HOST,
    PORT,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    try:
        await redis_manager.connect()
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    try:
        await redis_manager.disconnect()
    except Exception as e:
        print(f"❌ Shutdown error: {e}")


app = FastAPI(
    title="Khesht API",
    description="A simple MVP FastAPI application with OpenAI integration",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Khesht API is running!",
        "status": "healthy",
        "environment": ENVIRONMENT,
    }


@app.get("/user-prompt")
async def user_prompt(prompt: str, session_id: str = ""):
    """User prompt endpoint"""
    places, session_id, content = await get_suggestion_places_from_db(
        prompt, session_id
    )
    return {
        "tool_response": places,
        "session_id": session_id,
        "assistant_response": content,
    }


if __name__ == "__main__":
    print(f"🚀 Starting Khesht API on {HOST}:{PORT}")
    print(f"🌍 Environment: {ENVIRONMENT}")
    print(
        f"🔒 CORS Origins: {CORS_ORIGINS if not ALLOW_ALL_ORIGINS else 'All origins allowed'}"
    )

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        # Additional configurations
        reload=ENVIRONMENT == "development",
        access_log=True,
        # Security headers
        server_header=False,
        date_header=False,
    )
