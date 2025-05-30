import json
import uuid

from pydantic import BaseModel

from app.helper.openai_helper import openapi_service
from app.helper.chromadb_helper import chroma_db_service
from app.schema import Place
from app.services.chat_manager import chat_manager


class SuggestionPlaces(BaseModel):
    places: list[Place]


async def get_suggestion_places(
    prompt: str, session_id: str = ""
) -> tuple[list[Place], str]:
    if not session_id:
        session_id = str(uuid.uuid4())

    previous_messages = await chat_manager.get_session_messages(session_id)
    system_message = openapi_service.create_system_message(
        """
You are a travel assistant specialized in Iran. Recommend only real, verified, and bookable tourist accommodations or destinations in Iran based on user preferences.

## RULES:

- Use only these sources:
    - https://www.jabama.com/
    - https://www.jajiga.com/
    - https://www.shab.rentals/
    - https://www.otaghak.com/
    - https://www.vilajar.com/
- All website and image URLs must return HTTP 200
- Image URLs must point to real image files (.jpg, .jpeg, .png, .webp, .avif, etc.)
- If no valid image can be found, do not include an image URL
- Only include links that lead to a **real, bookable listing** with a **checkout/reservation button**
- Never use unverified or placeholder data
- Never use any other source not listed above

## FOR EACH DESTINATION, RETURN:

- Name
- Description
- Location (address or coordinates)
- Category (e.g., historical, natural, cultural)
- Best_time_to_visit
- Duration
- Accessibility
- Nearby_attractions
- Image_urls (only if valid)
- Official_website (must be from allowed sources and must include a checkout/reserve button)
- Additional_links (optional, only if valid, working, and from allowed sources)

## FINAL REMINDER:

Only include listings from approved sources that can be **actually reserved** online. Do not include any result unless the final page has a working **checkout/reservation button**.
"""
    )
    user_message = openapi_service.create_user_message(prompt)
    messages = [system_message] + previous_messages + [user_message]
    response = await openapi_service.send_chat_completion(
        messages,
        SuggestionPlaces,
        tools=[
            {
                "type": "web_search_preview",
                "search_context_size": "low",
            }
        ],
    )
    places = response.places
    assistant_message = openapi_service.create_assistant_message(
        f"suggestions places: {places}"
    )
    await chat_manager.save_session_messages(
        session_id, previous_messages + [assistant_message]
    )
    return places, session_id


async def get_suggestion_places_from_db(
    prompt: str, session_id: str = ""
) -> tuple[list[Place], str]:
    if not session_id:
        session_id = str(uuid.uuid4())

    previous_messages = await chat_manager.get_session_messages(session_id)
    system_message = openapi_service.create_system_message("""
You're a friendly and down-to-earth assistant helping people find lodges and villas, and plan their trips in Iran — all in Persian.
You speak naturally and kindly, like a real person having a helpful conversation.
You can use the following tool:
- query_similar_rooms: Use this to search for lodges and villas based on what the user needs.

""")
    user_message = openapi_service.create_user_message(prompt)
    messages = [system_message] + previous_messages + [user_message]
    response = openapi_service.chat_completions_create(
        messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "query_similar_rooms",
                    "description": "Search for lodges and villas based on user preferences",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query describing the desired accommodation",
                            }
                        },
                        "required": ["query"],
                    },
                },
            }
        ],
    ).choices[0].message

    places = []
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments
        if tool_name == "query_similar_rooms":
            query = json.loads(tool_args)["query"]
            print(f"query: {query}")
            places = chroma_db_service.query_similar_rooms(query, n_results=3)

            assistant_message = openapi_service.create_assistant_message(
                f"query: {query} \nsuggestions places: {places}"
            )
        await chat_manager.save_session_messages(
            session_id, previous_messages + [assistant_message]
        )
    else:
        assistant_message = openapi_service.create_assistant_message(
            f"{response.content}"
        )
        await chat_manager.save_session_messages(
            session_id, previous_messages + [assistant_message]
        )
    return places, session_id, response.content
