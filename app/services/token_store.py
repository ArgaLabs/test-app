"""Simple in-memory token store keyed by a session id.

In production you'd use a database or encrypted cookies.
"""
from __future__ import annotations

from dataclasses import dataclass, field

_store: dict[str, dict[str, TokenSet]] = {}


@dataclass
class TokenSet:
    access_token: str
    refresh_token: str = ""


def save(session_id: str, provider: str, tokens: TokenSet) -> None:
    _store.setdefault(session_id, {})[provider] = tokens


def get(session_id: str, provider: str) -> TokenSet | None:
    return _store.get(session_id, {}).get(provider)


def get_all(session_id: str) -> dict[str, TokenSet]:
    return _store.get(session_id, {})


def remove(session_id: str, provider: str) -> None:
    if session_id in _store:
        _store[session_id].pop(provider, None)
