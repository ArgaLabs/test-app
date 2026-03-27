"""Google Calendar API routes."""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.integrations import gcalendar_client
from app.services import token_store

router = APIRouter(prefix="/calendar", tags=["calendar"])


def _get_token(request: Request) -> str:
    session_id = request.cookies.get("session_id", "")
    ts = token_store.get(session_id, "google")
    if not ts:
        raise HTTPException(401, "Not connected to Google. Please authenticate first.")
    return ts.access_token


class EventCreate(BaseModel):
    summary: str
    start: str  # ISO 8601 datetime
    end: str
    description: str = ""
    location: str = ""


class EventUpdate(BaseModel):
    summary: str | None = None
    start: str | None = None
    end: str | None = None
    description: str | None = None
    location: str | None = None


@router.get("/events")
async def list_events(request: Request, time_min: str | None = None, max_results: int = 50):
    token = _get_token(request)
    events = gcalendar_client.list_events(token, max_results=max_results, time_min=time_min)
    return [asdict(e) for e in events]


@router.post("/events")
async def create_event(body: EventCreate, request: Request):
    token = _get_token(request)
    event = gcalendar_client.create_event(
        token,
        summary=body.summary,
        start=body.start,
        end=body.end,
        description=body.description,
        location=body.location,
    )
    return asdict(event)


@router.patch("/events/{event_id}")
async def update_event(event_id: str, body: EventUpdate, request: Request):
    token = _get_token(request)
    event = gcalendar_client.update_event(
        token,
        event_id=event_id,
        summary=body.summary,
        start=body.start,
        end=body.end,
        description=body.description,
        location=body.location,
    )
    return asdict(event)


@router.delete("/events/{event_id}")
async def delete_event(event_id: str, request: Request):
    token = _get_token(request)
    gcalendar_client.delete_event(token, event_id)
    return {"ok": True}
