"""Google Drive integration using the Google API Python Client."""
from __future__ import annotations

import io
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]


@dataclass
class FileInfo:
    id: str
    name: str
    mime_type: str
    size: int | None
    is_folder: bool
    modified: str | None


def build_credentials(access_token: str, refresh_token: str = "") -> Credentials:
    return Credentials(
        token=access_token,
        refresh_token=refresh_token,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
    )


def get_service(access_token: str, refresh_token: str = ""):
    creds = build_credentials(access_token, refresh_token)
    return build("drive", "v3", credentials=creds)


def list_files(access_token: str, folder_id: str = "root") -> list[FileInfo]:
    service = get_service(access_token)
    query = f"'{folder_id}' in parents and trashed=false"
    results = (
        service.files()
        .list(q=query, fields="files(id,name,mimeType,size,modifiedTime)", pageSize=100)
        .execute()
    )
    files = []
    for f in results.get("files", []):
        is_folder = f["mimeType"] == "application/vnd.google-apps.folder"
        files.append(
            FileInfo(
                id=f["id"],
                name=f["name"],
                mime_type=f["mimeType"],
                size=int(f["size"]) if f.get("size") else None,
                is_folder=is_folder,
                modified=f.get("modifiedTime"),
            )
        )
    return files


def upload_file(
    access_token: str, filename: str, content: bytes, mime_type: str, folder_id: str = "root"
) -> FileInfo:
    service = get_service(access_token)
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type, resumable=True)
    created = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id,name,mimeType,size,modifiedTime")
        .execute()
    )
    return FileInfo(
        id=created["id"],
        name=created["name"],
        mime_type=created["mimeType"],
        size=int(created["size"]) if created.get("size") else None,
        is_folder=False,
        modified=created.get("modifiedTime"),
    )


def delete_file(access_token: str, file_id: str) -> bool:
    service = get_service(access_token)
    service.files().delete(fileId=file_id).execute()
    return True


def rename_file(access_token: str, file_id: str, new_name: str) -> FileInfo:
    service = get_service(access_token)
    updated = (
        service.files()
        .update(fileId=file_id, body={"name": new_name}, fields="id,name,mimeType,size,modifiedTime")
        .execute()
    )
    return FileInfo(
        id=updated["id"],
        name=updated["name"],
        mime_type=updated["mimeType"],
        size=int(updated["size"]) if updated.get("size") else None,
        is_folder=updated["mimeType"] == "application/vnd.google-apps.folder",
        modified=updated.get("modifiedTime"),
    )
