from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from urllib.parse import urlencode
import httpx
from dotenv import load_dotenv
from backend.db.db import users_collection


# Ensure environment variables are loaded for local development
load_dotenv()

router = APIRouter()


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI]):
    raise RuntimeError("Missing required Google OAuth environment variables")

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"


@router.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2>Welcome to FastAPI Google OAuth2 Login</h2>
    <a href="/login">Login with Google</a>
    """


@router.get("/login")
def login():
    query_params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(query_params)}"
    return RedirectResponse(url)


@router.get("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")

    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
        token_response.raise_for_status()
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        print(token_data)

        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to retrieve access token")

        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = await client.get(GOOGLE_USERINFO_ENDPOINT, headers=headers)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

    # Persist or update the user in the database
    provider = "google"
    provider_id = userinfo.get("id")
    email = userinfo.get("email")
    name = userinfo.get("name")

    if not provider_id or not email:
        raise HTTPException(status_code=400, detail="Missing required user information from provider")

    # Upsert user by provider + provider_id
    upsert_result = await users_collection.update_one(
        {"provider": provider, "provider_id": provider_id},
        {
            "$set": {"name": name, "email": email},
            "$setOnInsert": {"provider": provider, "provider_id": provider_id},
        },
        upsert=True,
    )

    user_id = upsert_result.upserted_id

    return RedirectResponse(
        f"/profile?name={name}&email={email}&picture={userinfo.get('picture','')}{'&id='+str(user_id) if user_id else ''}"
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    user_info = request.query_params
    name = user_info.get("name")
    email = user_info.get("email")
    picture = user_info.get("picture")

    return f"""
    <html>
        <head><title>User Profile</title></head>
        <body style='text-align:center; font-family:sans-serif;'>
            <h1>Welcome, {name}!</h1>
            <img src="{picture}" alt="Profile Picture" width="120"/><br>
            <p>Email: {email}</p>
        </body>
    </html>
    """


