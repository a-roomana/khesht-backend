from pydantic import BaseModel, Field


class UserPromptRequest(BaseModel):
    """Request body for user prompt"""

    prompt: str
    session_id: str | None = Field(default="")



class Place(BaseModel):
    """Place model"""

    title: str
    description: str
    web_url: str
    image_urls: list[str] | None = Field(default_factory=list)
    rating: float = None
    review_count: int = 0
    price: int = 0


class UserPromptResponse(BaseModel):
    """Response body for user prompt"""

    places: list[Place]
    session_id: str
