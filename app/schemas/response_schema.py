from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent's response to the user")
    status: str = Field(default="success", description="Response status")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    status: str = Field(default="error", description="Response status")