from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.helper.redis_helper import redis_manager
from app.services.chat_service import get_suggestion_places_from_db

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


@app.get("/user-prompt")
async def user_prompt(prompt: str, session_id: str=""):
    """User prompt endpoint"""
    places, session_id, content = await  get_suggestion_places_from_db(prompt, session_id)
    return {"tool_response": places, "session_id": session_id, "assistant_response": content}
    # return UserPromptResponse(places=places, session_id=session_id)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
