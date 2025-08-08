from typing import Annotated, List, Optional
from datetime import datetime
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


PyObjectId = Annotated[str, BeforeValidator(str)]


class TokenModel(BaseModel):
    """Token/session document stored in a separate collection.

    Notes:
    - `refresh_token_enc` is the encrypted refresh token, never store raw token
    - `scopes` is the list of granted scopes
    - `revoked_at` is null until revoked
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: Optional[PyObjectId] = Field(default=None, description="Owner user id")
    provider: str = Field(..., description="OAuth provider, e.g. 'google'")
    scopes: List[str] = Field(default_factory=list)
    refresh_token_enc: Optional[str] = Field(default=None)

    # Optional session metadata (allow multiple refresh tokens per user/device)
    session_id: Optional[str] = None
    device_info: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_refresh_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_id": "665a2d9f3c0a5e3f1a2b3c4d",
                "provider": "google",
                "scopes": ["openid", "email", "profile"],
                "refresh_token_enc": "gAAAAABk...",
                "session_id": "device-123",
                "device_info": "Chrome on macOS",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "last_refresh_at": None,
                "revoked_at": None,
            }
        },
    )