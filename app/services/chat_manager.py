import json

from app.helper.openai_helper import OpenAIMessage, OpendAIRole
from app.helper.redis_helper import redis_manager


class ChatManager:
    def __init__(self):
        self.session_prefix = "chat_session:"

    def _get_session_key(self, session_id: str) -> str:
        """Generate Redis key for session"""
        return f"{self.session_prefix}{session_id}"

    def _serialize_message(self, message: OpenAIMessage) -> dict:
        """Convert OpenAIMessage to serializable dict"""
        return {"role": message.role.value, "content": message.content}

    def _deserialize_message(self, message_dict: dict) -> OpenAIMessage:
        """Convert dict back to OpenAIMessage"""
        return OpenAIMessage(
            role=OpendAIRole(message_dict["role"]), content=message_dict["content"]
        )

    async def get_session_messages(self, session_id: str) -> list[OpenAIMessage]:
        """Retrieve all messages for a session"""
        try:
            redis_client = await redis_manager.get_client()
            session_key = self._get_session_key(session_id)
            messages_json = await redis_client.get(session_key)

            if messages_json is None:
                return []

            messages_data = json.loads(messages_json)
            return [self._deserialize_message(msg) for msg in messages_data]

        except Exception as e:
            # Log the error in a real application
            print(f"Error retrieving messages for session {session_id}: {e}")
            return []

    async def save_session_messages(
        self, session_id: str, messages: list[OpenAIMessage]
    ) -> None:
        """Save messages for a session"""
        try:
            redis_client = await redis_manager.get_client()
            session_key = self._get_session_key(session_id)
            messages_data = [self._serialize_message(msg) for msg in messages]
            messages_json = json.dumps(messages_data)

            # Set with expiration (24 hours = 86400 seconds)
            await redis_client.setex(session_key, 86400, messages_json)

        except Exception as e:
            # Log the error in a real application
            print(f"Error saving messages for session {session_id}: {e}")
            raise


chat_manager = ChatManager()
