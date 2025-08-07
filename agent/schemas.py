from typing import Literal
from langchain_core.pydantic_v1 import BaseModel


class RouterSchema(BaseModel):
    """Schema for the router decision."""

    classification: Literal[
        "application_tracking",
        "interview_prep",
        "calendar",
        "resume_assistant",
        "general",
    ]
