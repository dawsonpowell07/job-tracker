from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.routers.users import router as users_router
from backend.routers.auth import router as auth_router
from backend.db.db import init_indexes, ping, close_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await ping()
    await init_indexes()
    try:
        yield
    finally:
        # Shutdown
        close_client()


app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(users_router)
app.include_router(auth_router)