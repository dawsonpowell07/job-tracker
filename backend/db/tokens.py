from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from bson import ObjectId

from backend.db.db import tokens_collection


UserId = Union[str, ObjectId]
TokenId = Union[str, ObjectId]


def _as_object_id(value: TokenId) -> ObjectId:
    return value if isinstance(value, ObjectId) else ObjectId(str(value))


def _normalize_user_id(user_id: UserId) -> ObjectId:
    return user_id if isinstance(user_id, ObjectId) else ObjectId(str(user_id))


async def get_active_token(user_id: UserId, provider: str) -> Optional[dict]:
    return await tokens_collection.find_one(
        {"user_id": _normalize_user_id(user_id), "provider": provider, "revoked_at": None}
    )


async def save_or_rotate_token(
    user_id: UserId,
    provider: str,
    scopes: Optional[List[str]] = None,
    refresh_token_enc: Optional[str] = None,
    *,
    session_id: Optional[str] = None,
    device_info: Optional[str] = None,
) -> dict:
    """Insert new or update existing token document for a user+provider.

    - If `refresh_token_enc` is provided, it replaces the existing encrypted token (rotation).
    - If only `scopes` are provided, updates scopes if a token exists.
    - Creates a new document if none exists and `refresh_token_enc` is provided.
    Returns the up-to-date token document.
    """
    now = datetime.now(timezone.utc)
    existing = await get_active_token(user_id, provider)

    if existing is None:
        if refresh_token_enc is None:
            # No existing token and nothing to save
            return {
                "user_id": _normalize_user_id(user_id),
                "provider": provider,
                "scopes": scopes or [],
                "refresh_token_enc": None,
                "created_at": now,
                "updated_at": now,
                "last_refresh_at": None,
                "revoked_at": None,
                "session_id": session_id,
                "device_info": device_info,
            }
        doc = {
            "user_id": _normalize_user_id(user_id),
            "provider": provider,
            "scopes": scopes or [],
            "refresh_token_enc": refresh_token_enc,
            "created_at": now,
            "updated_at": now,
            "last_refresh_at": None,
            "revoked_at": None,
            "session_id": session_id,
            "device_info": device_info,
        }
        insert_result = await tokens_collection.insert_one(doc)
        doc["_id"] = insert_result.inserted_id
        return doc

    # Update existing document
    update_fields: Dict[str, Any] = {"updated_at": now}
    if scopes is not None:
        update_fields["scopes"] = scopes
    if refresh_token_enc is not None:
        update_fields["refresh_token_enc"] = refresh_token_enc
    if session_id is not None:
        update_fields["session_id"] = session_id
    if device_info is not None:
        update_fields["device_info"] = device_info

    await tokens_collection.update_one(
        {"_id": existing["_id"]}, {"$set": update_fields}
    )
    updated_doc = await tokens_collection.find_one({"_id": existing["_id"]})
    if updated_doc is None:
        raise RuntimeError("Updated token document not found")
    return updated_doc


async def update_last_refresh_at(token_id: TokenId, when: Optional[datetime] = None) -> bool:
    when = when or datetime.now(timezone.utc)
    result = await tokens_collection.update_one(
        {"_id": _as_object_id(token_id)}, {"$set": {"last_refresh_at": when, "updated_at": when}}
    )
    return result.modified_count > 0


async def revoke_token(token_id: TokenId, when: Optional[datetime] = None) -> bool:
    when = when or datetime.now(timezone.utc)
    result = await tokens_collection.update_one(
        {"_id": _as_object_id(token_id)}, {"$set": {"revoked_at": when, "updated_at": when}}
    )
    return result.modified_count > 0


async def delete_tokens_for_user(user_id: UserId, provider: Optional[str] = None) -> int:
    query: dict = {"user_id": _normalize_user_id(user_id)}
    if provider:
        query["provider"] = provider
    result = await tokens_collection.delete_many(query)
    return result.deleted_count or 0