"""Unified file management API — list, upload, delete, rename across providers."""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form

from app.services import token_store
from app.services.slack_notify import notify
from app.integrations import dropbox_client, box_client, gdrive_client

router = APIRouter(prefix="/files", tags=["files"])


def _get_token(request: Request, provider: str) -> str:
    session_id = request.cookies.get("session_id", "")
    ts = token_store.get(session_id, provider)
    if not ts:
        raise HTTPException(status_code=401, detail=f"Not connected to {provider}. Please authenticate first.")
    return ts.access_token


# ── List ────────────────────────────────────────────────────────────
@router.get("/{provider}")
async def list_files(provider: str, request: Request, path: str = "", folder_id: str = ""):
    token = _get_token(request, provider)
    if provider == "dropbox":
        items = dropbox_client.list_files(token, path or "")
    elif provider == "box":
        items = box_client.list_files(token, folder_id or "0")
    elif provider == "google":
        items = gdrive_client.list_files(token, folder_id or "root")
    else:
        raise HTTPException(400, "Unknown provider")
    return [asdict(f) for f in items]


# ── Upload ──────────────────────────────────────────────────────────
@router.post("/{provider}/upload")
async def upload_file(
    provider: str,
    request: Request,
    file: UploadFile = File(...),
    path: str = Form(""),
    folder_id: str = Form(""),
):
    token = _get_token(request, provider)
    content = await file.read()
    filename = file.filename or "untitled"

    if provider == "dropbox":
        dest = f"{path}/{filename}" if path else f"/{filename}"
        result = dropbox_client.upload_file(token, dest, content)
    elif provider == "box":
        result = box_client.upload_file(token, folder_id or "0", filename, content)
    elif provider == "google":
        mime = file.content_type or "application/octet-stream"
        result = gdrive_client.upload_file(token, filename, content, mime, folder_id or "root")
    else:
        raise HTTPException(400, "Unknown provider")

    notify("upload", provider, filename)
    return asdict(result)


# ── Delete ──────────────────────────────────────────────────────────
@router.delete("/{provider}")
async def delete_file(
    provider: str,
    request: Request,
    path: str = "",
    file_id: str = "",
    is_folder: bool = False,
):
    token = _get_token(request, provider)
    name = path or file_id

    if provider == "dropbox":
        if not path:
            raise HTTPException(400, "path is required for Dropbox")
        dropbox_client.delete_file(token, path)
    elif provider == "box":
        if not file_id:
            raise HTTPException(400, "file_id is required for Box")
        box_client.delete_file(token, file_id, is_folder)
    elif provider == "google":
        if not file_id:
            raise HTTPException(400, "file_id is required for Google Drive")
        gdrive_client.delete_file(token, file_id)
    else:
        raise HTTPException(400, "Unknown provider")

    notify("delete", provider, name)
    return {"ok": True}


# ── Rename ──────────────────────────────────────────────────────────
@router.patch("/{provider}/rename")
async def rename_file(
    provider: str,
    request: Request,
    old_path: str = "",
    new_path: str = "",
    file_id: str = "",
    new_name: str = "",
    is_folder: bool = False,
):
    token = _get_token(request, provider)

    if provider == "dropbox":
        if not old_path or not new_path:
            raise HTTPException(400, "old_path and new_path required for Dropbox")
        result = dropbox_client.rename_file(token, old_path, new_path)
    elif provider == "box":
        if not file_id or not new_name:
            raise HTTPException(400, "file_id and new_name required for Box")
        result = box_client.rename_file(token, file_id, new_name, is_folder)
    elif provider == "google":
        if not file_id or not new_name:
            raise HTTPException(400, "file_id and new_name required for Google Drive")
        result = gdrive_client.rename_file(token, file_id, new_name)
    else:
        raise HTTPException(400, "Unknown provider")

    notify("rename", provider, new_name or new_path, f"from {old_path or file_id}")
    return asdict(result)
