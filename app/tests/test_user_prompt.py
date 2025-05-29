import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.helper.openai_helper import OpenAIMessage, OpendAIRole
from app.main import app
from app.schema import Place, UserPromptResponse
from app.services.chat_service import SuggestionPlaces

from .config import *  # noqa: F403


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_user_prompt():
    """Sample user prompt for testing"""
    return {
        "prompt": "What are some good restaurants in New York?",
        "session_id": "test-session-123",
    }


@pytest.fixture
def sample_places():
    """Sample places response from GPT"""
    return [
        Place(
            name="Joe's Pizza",
            description="Famous New York pizza spot",
            image_urls=["https://example.com/joes.jpg"],
            urls=["https://joes-pizza.com"],
        ),
        Place(
            name="Katz's Delicatessen",
            description="Iconic NYC deli serving pastrami",
            image_urls=["https://example.com/katz.jpg"],
            urls=["https://katzdeli.com"],
        ),
    ]


@pytest.fixture
def existing_session_messages():
    """Mock existing messages from Redis for a session"""
    return [
        OpenAIMessage(role=OpendAIRole.USER, content="Tell me about NYC food"),
        OpenAIMessage(
            role=OpendAIRole.ASSISTANT, content="NYC has amazing diverse food scene"
        ),
    ]


@pytest.fixture
def mock_gpt_response(sample_places):
    """Mock GPT response"""
    return SuggestionPlaces(places=sample_places)


class TestUserPromptMainFlow:
    """Test the main business logic flow of the user-prompt endpoint"""

    @patch("app.services.chat_manager.chat_manager.get_session_messages")
    @patch("app.services.chat_manager.chat_manager.save_session_messages")
    @patch("app.helper.openai_helper.openapi_service.send_chat_completion")
    def test_main_flow_with_existing_session(
        self,
        mock_send_completion,
        mock_save_messages,
        mock_get_messages,
        client,
        sample_user_prompt,
        existing_session_messages,
        mock_gpt_response,
    ):
        """Test main flow: get old messages -> create new messages -> request GPT -> store response"""

        # Setup mocks
        mock_get_messages.return_value = existing_session_messages
        mock_send_completion.return_value = mock_gpt_response
        mock_save_messages.return_value = None

        # Make request
        response = client.post("/user-prompt", json=sample_user_prompt)

        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        assert "places" in response_data
        assert len(response_data["places"]) == 2
        assert response_data["places"][0]["name"] == "Joe's Pizza"

        # Verify the flow was executed correctly

        # 1. Should retrieve old messages from Redis
        mock_get_messages.assert_called_once_with("test-session-123")

        # 2. Should send messages to GPT (system + old messages + new user message)
        mock_send_completion.assert_called_once()
        call_args = mock_send_completion.call_args[0]
        messages_sent = call_args[0]

        # Should have system message + existing messages + new user message
        assert len(messages_sent) >= 4  # system + 2 existing + 1 new user message
        assert messages_sent[0].role == OpendAIRole.SYSTEM
        assert messages_sent[-1].role == OpendAIRole.USER
        assert (
            messages_sent[-1].content == "What are some good restaurants in New York?"
        )

        # 3. Should save new messages to Redis (old + new assistant message)
        mock_save_messages.assert_called_once()
        save_call_args = mock_save_messages.call_args
        session_id = save_call_args[0][0]
        saved_messages = save_call_args[0][1]

        assert session_id == "test-session-123"
        # Should save existing messages + new assistant message
        assert len(saved_messages) >= len(existing_session_messages)

    @patch("app.services.chat_manager.chat_manager.get_session_messages")
    @patch("app.services.chat_manager.chat_manager.save_session_messages")
    @patch("app.helper.openai_helper.openapi_service.send_chat_completion")
    def test_main_flow_with_new_session(
        self,
        mock_send_completion,
        mock_save_messages,
        mock_get_messages,
        client,
        sample_user_prompt,
        mock_gpt_response,
    ):
        """Test main flow with new session (no existing messages)"""

        # Setup mocks - new session has no messages
        mock_get_messages.return_value = []
        mock_send_completion.return_value = mock_gpt_response
        mock_save_messages.return_value = None

        # Make request
        response = client.post("/user-prompt", json=sample_user_prompt)

        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["places"]) == 2

        # Verify flow
        mock_get_messages.assert_called_once_with("test-session-123")

        # Should send system message + user message only (no existing messages)
        mock_send_completion.assert_called_once()
        call_args = mock_send_completion.call_args[0]
        messages_sent = call_args[0]

        # Should have system message + new user message
        assert len(messages_sent) == 2
        assert messages_sent[0].role == OpendAIRole.SYSTEM
        assert messages_sent[1].role == OpendAIRole.USER

        # Should save assistant message
        mock_save_messages.assert_called_once()

    @patch("app.services.chat_manager.chat_manager.get_session_messages")
    @patch("app.services.chat_manager.chat_manager.save_session_messages")
    @patch("app.helper.openai_helper.openapi_service.send_chat_completion")
    def test_main_flow_without_session_id(
        self,
        mock_send_completion,
        mock_save_messages,
        mock_get_messages,
        client,
        mock_gpt_response,
    ):
        """Test main flow when no session_id is provided"""

        # Setup mocks
        mock_get_messages.return_value = []
        mock_send_completion.return_value = mock_gpt_response
        mock_save_messages.return_value = None

        # Request without session_id
        request_data = {
            "prompt": "What are some good restaurants in New York?",
            "session_id": "",  # Empty session_id
        }

        # Make request
        response = client.post("/user-prompt", json=request_data)

        # Verify response
        assert response.status_code == 200

        # Verify flow still works with empty session_id
        mock_get_messages.assert_called_once_with("")
        mock_send_completion.assert_called_once()
        mock_save_messages.assert_called_once()

    @patch("app.services.chat_manager.chat_manager.get_session_messages")
    @patch("app.services.chat_manager.chat_manager.save_session_messages")
    @patch("app.helper.openai_helper.openapi_service.send_chat_completion")
    def test_redis_and_gpt_integration(
        self,
        mock_send_completion,
        mock_save_messages,
        mock_get_messages,
        client,
        sample_user_prompt,
        existing_session_messages,
        mock_gpt_response,
    ):
        """Test that Redis messages are properly integrated with GPT request"""

        # Setup mocks
        mock_get_messages.return_value = existing_session_messages
        mock_send_completion.return_value = mock_gpt_response
        mock_save_messages.return_value = None

        # Make request
        response = client.post("/user-prompt", json=sample_user_prompt)

        assert response.status_code == 200

        # Verify that existing messages from Redis are included in GPT request
        call_args = mock_send_completion.call_args[0]
        messages_sent = call_args[0]

        # Should contain the existing messages from Redis
        user_messages = [msg for msg in messages_sent if msg.role == OpendAIRole.USER]
        assistant_messages = [
            msg for msg in messages_sent if msg.role == OpendAIRole.ASSISTANT
        ]

        # Should have both old and new user messages
        assert len(user_messages) >= 2
        assert "Tell me about NYC food" in [msg.content for msg in user_messages]
        assert "What are some good restaurants in New York?" in [
            msg.content for msg in user_messages
        ]

        # Should have old assistant message
        assert len(assistant_messages) >= 1
        assert "NYC has amazing diverse food scene" in [
            msg.content for msg in assistant_messages
        ]

    def test_response_format_validation(self, client, sample_user_prompt):
        """Test that response follows the expected UserPromptResponse schema"""

        # Mock the GPT response
        with patch(
            "app.helper.openai_helper.openapi_service.send_chat_completion"
        ) as mock_gpt:
            mock_places = [
                Place(
                    name="Test Restaurant",
                    description="Test description",
                    image_urls=["http://test.com/img.jpg"],
                    urls=["http://test.com"],
                )
            ]
            mock_gpt.return_value = SuggestionPlaces(places=mock_places)

            response = client.post("/user-prompt", json=sample_user_prompt)

            assert response.status_code == 200
            data = response.json()

            # Validate response structure
            validated_response = UserPromptResponse(**data)
            assert len(validated_response.places) == 1
            assert validated_response.places[0].name == "Test Restaurant"
