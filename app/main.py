"""Test-App — Unified file management, document parsing & calendar."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, files, calendar, documents
from app.config import FRONTEND_URL

app = FastAPI(title="Test App", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(calendar.router)
app.include_router(documents.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
