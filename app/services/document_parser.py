"""Document parsing via the Unstructured API."""
from __future__ import annotations

import httpx

from app.config import UNSTRUCTURED_API_KEY, UNSTRUCTURED_API_URL


async def parse_document(filename: str, content: bytes, content_type: str) -> list[dict]:
    """Send a document to Unstructured and return the parsed elements."""
    headers = {}
    if UNSTRUCTURED_API_KEY:
        headers["unstructured-api-key"] = UNSTRUCTURED_API_KEY

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            UNSTRUCTURED_API_URL,
            headers=headers,
            files={"files": (filename, content, content_type)},
            data={"strategy": "auto"},
        )
        resp.raise_for_status()
        return resp.json()
