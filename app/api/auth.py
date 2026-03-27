"""OAuth2 callback routes for Dropbox, Box, and Google."""
from __future__ import annotations

import secrets
import urllib.parse

from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from app.config import (
    API_URL,
    BOX_CLIENT_ID,
    BOX_CLIENT_SECRET,
    DROPBOX_APP_KEY,
    DROPBOX_APP_SECRET,
    FRONTEND_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
)
from app.services.token_store import TokenSet, save

import httpx

router = APIRouter(prefix="/auth", tags=["auth"])

# ── Dropbox ─────────────────────────────────────────────────────────
DROPBOX_AUTH_URL = "https://www.dropbox.com/oauth2/authorize"
DROPBOX_TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"


@router.get("/dropbox")
async def dropbox_login(request: Request):
    params = {
        "client_id": DROPBOX_APP_KEY,
        "redirect_uri": f"{API_URL}/auth/dropbox/callback",
        "response_type": "code",
        "token_access_type": "offline",
    }
    return RedirectResponse(f"{DROPBOX_AUTH_URL}?{urllib.parse.urlencode(params)}")


@router.get("/dropbox/callback")
async def dropbox_callback(code: str, request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            DROPBOX_TOKEN_URL,
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{API_URL}/auth/dropbox/callback",
            },
            auth=(DROPBOX_APP_KEY, DROPBOX_APP_SECRET),
        )
        resp.raise_for_status()
        data = resp.json()

    session_id = request.cookies.get("session_id", secrets.token_urlsafe(32))
    save(session_id, "dropbox", TokenSet(access_token=data["access_token"], refresh_token=data.get("refresh_token", "")))

    response = RedirectResponse(f"{FRONTEND_URL}/files?provider=dropbox")
    response.set_cookie("session_id", session_id, httponly=True, samesite="lax", max_age=86400 * 7)
    return response


# ── Box ─────────────────────────────────────────────────────────────
BOX_AUTH_URL = "https://account.box.com/api/oauth2/authorize"
BOX_TOKEN_URL = "https://api.box.com/oauth2/token"


@router.get("/box")
async def box_login():
    params = {
        "client_id": BOX_CLIENT_ID,
        "redirect_uri": f"{API_URL}/auth/box/callback",
        "response_type": "code",
    }
    return RedirectResponse(f"{BOX_AUTH_URL}?{urllib.parse.urlencode(params)}")


@router.get("/box/callback")
async def box_callback(code: str, request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            BOX_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": BOX_CLIENT_ID,
                "client_secret": BOX_CLIENT_SECRET,
                "redirect_uri": f"{API_URL}/auth/box/callback",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    session_id = request.cookies.get("session_id", secrets.token_urlsafe(32))
    save(session_id, "box", TokenSet(access_token=data["access_token"], refresh_token=data.get("refresh_token", "")))

    response = RedirectResponse(f"{FRONTEND_URL}/files?provider=box")
    response.set_cookie("session_id", session_id, httponly=True, samesite="lax", max_age=86400 * 7)
    return response


# ── Google (Drive + Calendar) ───────────────────────────────────────
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = "https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar"


@router.get("/google")
async def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": f"{API_URL}/auth/google/callback",
        "response_type": "code",
        "scope": GOOGLE_SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}")


@router.get("/google/callback")
async def google_callback(code: str, request: Request):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{API_URL}/auth/google/callback",
                "grant_type": "authorization_code",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    session_id = request.cookies.get("session_id", secrets.token_urlsafe(32))
    save(session_id, "google", TokenSet(access_token=data["access_token"], refresh_token=data.get("refresh_token", "")))

    response = RedirectResponse(f"{FRONTEND_URL}/files?provider=google")
    response.set_cookie("session_id", session_id, httponly=True, samesite="lax", max_age=86400 * 7)
    return response


# ── Status ──────────────────────────────────────────────────────────
@router.get("/status")
async def auth_status(request: Request):
    """Return which providers are connected for this session."""
    from app.services.token_store import get_all

    session_id = request.cookies.get("session_id", "")
    tokens = get_all(session_id)
    return {"connected": list(tokens.keys())}


@router.post("/disconnect/{provider}")
async def disconnect(provider: str, request: Request):
    from app.services.token_store import remove

    session_id = request.cookies.get("session_id", "")
    remove(session_id, provider)
    return {"ok": True}
