from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.helper.redis_helper import redis_manager
from app.services.chat_service import get_suggestion_places

from .schema import UserPromptRequest, UserPromptResponse


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


@app.post("/user-prompt")
async def user_prompt(user_prompt: UserPromptRequest) -> UserPromptResponse:
    """User prompt endpoint"""
    places, session_id = await  get_suggestion_places(user_prompt.prompt, user_prompt.session_id)
    return UserPromptResponse(places=places, session_id=session_id)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
