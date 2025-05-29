from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from app import settings

T = TypeVar("T", bound=BaseModel)


class OpendAIRole(StrEnum):
    """Enum for message roles in OpenAI chat completion"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(slots=True, frozen=True)
class OpenAIMessage:
    """Dataclass for OpenAI chat messages"""

    role: OpendAIRole
    content: str


class OpenAIService:
    """Service class for OpenAI API interactions with structured data"""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def create_message(self, role: OpendAIRole, content: str) -> OpenAIMessage:
        """Create a structured message"""
        return OpenAIMessage(role=role, content=content)

    def messages_to_dict(self, messages: list[OpenAIMessage]) -> list[dict]:
        """Convert Message dataclasses to dictionary format for OpenAI API"""
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]

    async def send_chat_completion(
        self, messages: list[OpenAIMessage], response_format: T, tools: list[dict]=None
    ) -> T:
        """Send structured chat completion request to OpenAI"""
        try:
            # Convert messages to dict format
            message_dicts = self.messages_to_dict(messages)

            # Send request to OpenAI
            response = self.client.responses.parse(
                model="gpt-4o",
                input=message_dicts,
                text_format=response_format,
                tools=tools,
            )
            return response.output_parsed
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")

    def create_system_message(self, content: str) -> OpenAIMessage:
        """Helper to create system message"""
        return self.create_message(OpendAIRole.SYSTEM, content)

    def create_user_message(self, content: str) -> OpenAIMessage:
        """Helper to create user message"""
        return self.create_message(OpendAIRole.USER, content)

    def create_assistant_message(self, content: str) -> OpenAIMessage:
        """Helper to create assistant message"""
        return self.create_message(OpendAIRole.ASSISTANT, content)


openapi_service = OpenAIService(api_key=settings.OPENAI_API_KEY)
