"""Application-wide MongoDB setup (async via Motor).

This module exposes a singleton Mongo client and database, ready to be imported
and used anywhere in the app. It also provides convenience helpers for:

- Getting collections and the database instance
- FastAPI dependency injection of the database
- Health checks (ping)
- Index initialization for known collections

Env vars used:
- MONGO_URI: Mongo connection string
- MONGODB_DATABASE or MONGO_DB: Database name
"""

from __future__ import annotations

from typing import AsyncIterator

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from starlette.config import Config

import os
print("CWD:", os.getcwd())
print("Exists:", os.path.exists(".env"))

# Read environment variables (falls back to .env in local dev)
_config = Config(".env")


def _get_required_config(*names: str) -> str:
    """Return the first present, non-empty config value among names.

    Raises RuntimeError if none are provided.
    """
    for name in names:
        try:
            value = _config(name)
        except Exception:
            value = None
        if value:
            return value
    tried = ", ".join(names)
    raise RuntimeError(f"Missing required environment variable(s): {tried}")


# Create a single, module-level client and database for reuse
_MONGO_URI: str = _get_required_config("MONGO_URI")
_MONGO_DB_NAME: str = _get_required_config("MONGODB_DATABASE", "MONGO_DB")

client: AsyncIOMotorClient = AsyncIOMotorClient(
    _MONGO_URI,
    uuidRepresentation="standard",
    tz_aware=True,
    serverSelectionTimeoutMS=5000,
)

db: AsyncIOMotorDatabase = client.get_database(_MONGO_DB_NAME)

# Commonly used collections
users_collection: AsyncIOMotorCollection = db.get_collection("users")
tokens_collection: AsyncIOMotorCollection = db.get_collection("tokens")


def get_database() -> AsyncIOMotorDatabase:
    """Return the shared database instance."""
    return db


def get_collection(name: str) -> AsyncIOMotorCollection:
    """Return a collection by name from the shared database."""
    return db.get_collection(name)


async def mongo_db_dependency() -> AsyncIterator[AsyncIOMotorDatabase]:
    """FastAPI dependency that yields the shared database instance."""
    yield db


async def ping() -> bool:
    """Ping the database to verify connectivity. Returns True on success."""
    try:
        await db.command("ping")
        return True
    except Exception:
        return False


async def init_indexes() -> None:
    """Create indexes required by the application (idempotent)."""
    # Unique user identity per provider
    await users_collection.create_index(
        [("provider", 1), ("provider_id", 1)],
        unique=True,
        name="provider_providerId_unique",
    )

    # Token/session indexes
    await tokens_collection.create_index(
        [("user_id", 1), ("provider", 1)],
        name="user_provider_idx",
        unique=False,
    )
    await tokens_collection.create_index(
        [("session_id", 1)],
        name="session_idx",
        unique=False,
    )
    await tokens_collection.create_index(
        [("revoked_at", 1)],
        name="revoked_idx",
        unique=False,
    )


def close_client() -> None:
    """Close the shared Mongo client (use on application shutdown)."""
    try:
        client.close()
    except Exception:
        # Best-effort close; ignore errors on shutdown
        pass

__all__ = [
    "client",
    "db",
    "users_collection",
    "tokens_collection",
    "get_database",
    "get_collection",
    "mongo_db_dependency",
    "ping",
    "init_indexes",
    "close_client"
]