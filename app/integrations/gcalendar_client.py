"""Google Calendar integration using Google API Python Client."""
from __future__ import annotations

from dataclasses import dataclass

from googleapiclient.discovery import build

from app.integrations.gdrive_client import build_credentials


@dataclass
class CalendarEvent:
    id: str
    summary: str
    start: str
    end: str
    description: str | None
    location: str | None


def get_service(access_token: str, refresh_token: str = ""):
    creds = build_credentials(access_token, refresh_token)
    return build("calendar", "v3", credentials=creds)


def list_events(
    access_token: str,
    calendar_id: str = "primary",
    max_results: int = 50,
    time_min: str | None = None,
) -> list[CalendarEvent]:
    service = get_service(access_token)
    params: dict = {
        "calendarId": calendar_id,
        "maxResults": max_results,
        "singleEvents": True,
        "orderBy": "startTime",
    }
    if time_min:
        params["timeMin"] = time_min
    results = service.events().list(**params).execute()
    events = []
    for e in results.get("items", []):
        start = e.get("start", {})
        end = e.get("end", {})
        events.append(
            CalendarEvent(
                id=e["id"],
                summary=e.get("summary", "(No title)"),
                start=start.get("dateTime", start.get("date", "")),
                end=end.get("dateTime", end.get("date", "")),
                description=e.get("description"),
                location=e.get("location"),
            )
        )
    return events


def create_event(
    access_token: str,
    summary: str,
    start: str,
    end: str,
    description: str = "",
    location: str = "",
    calendar_id: str = "primary",
) -> CalendarEvent:
    service = get_service(access_token)
    body = {
        "summary": summary,
        "start": {"dateTime": start},
        "end": {"dateTime": end},
    }
    if description:
        body["description"] = description
    if location:
        body["location"] = location

    created = service.events().insert(calendarId=calendar_id, body=body).execute()
    return CalendarEvent(
        id=created["id"],
        summary=created.get("summary", ""),
        start=created["start"].get("dateTime", created["start"].get("date", "")),
        end=created["end"].get("dateTime", created["end"].get("date", "")),
        description=created.get("description"),
        location=created.get("location"),
    )


def update_event(
    access_token: str,
    event_id: str,
    summary: str | None = None,
    start: str | None = None,
    end: str | None = None,
    description: str | None = None,
    location: str | None = None,
    calendar_id: str = "primary",
) -> CalendarEvent:
    service = get_service(access_token)
    existing = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

    if summary is not None:
        existing["summary"] = summary
    if start is not None:
        existing["start"] = {"dateTime": start}
    if end is not None:
        existing["end"] = {"dateTime": end}
    if description is not None:
        existing["description"] = description
    if location is not None:
        existing["location"] = location

    updated = (
        service.events().update(calendarId=calendar_id, eventId=event_id, body=existing).execute()
    )
    return CalendarEvent(
        id=updated["id"],
        summary=updated.get("summary", ""),
        start=updated["start"].get("dateTime", updated["start"].get("date", "")),
        end=updated["end"].get("dateTime", updated["end"].get("date", "")),
        description=updated.get("description"),
        location=updated.get("location"),
    )


def delete_event(access_token: str, event_id: str, calendar_id: str = "primary") -> bool:
    service = get_service(access_token)
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return True
