"""Dropbox integration using the official Dropbox Python SDK."""
from __future__ import annotations

import io
from dataclasses import dataclass

import dropbox
from dropbox.files import FileMetadata, FolderMetadata, WriteMode
from dropbox.oauth import DropboxOAuth2Flow

from app.config import API_URL, DROPBOX_APP_KEY, DROPBOX_APP_SECRET


@dataclass
class FileInfo:
    id: str
    name: str
    path: str
    size: int | None
    is_folder: bool
    modified: str | None


def get_auth_flow(session: dict) -> DropboxOAuth2Flow:
    """Create an OAuth2 authorization flow."""
    return DropboxOAuth2Flow(
        consumer_key=DROPBOX_APP_KEY,
        consumer_secret=DROPBOX_APP_SECRET,
        redirect_uri=f"{API_URL}/auth/dropbox/callback",
        session=session,
        csrf_token_session_key="dropbox-auth-csrf-token",
        token_access_type="offline",
    )


def get_client(access_token: str) -> dropbox.Dropbox:
    return dropbox.Dropbox(oauth2_access_token=access_token)


def list_files(access_token: str, path: str = "") -> list[FileInfo]:
    dbx = get_client(access_token)
    result = dbx.files_list_folder(path)
    files = []
    for entry in result.entries:
        is_folder = isinstance(entry, FolderMetadata)
        files.append(
            FileInfo(
                id=entry.id,
                name=entry.name,
                path=entry.path_display,
                size=getattr(entry, "size", None),
                is_folder=is_folder,
                modified=getattr(entry, "server_modified", None)
                and str(entry.server_modified)
                if isinstance(entry, FileMetadata)
                else None,
            )
        )
    return files


def upload_file(access_token: str, path: str, content: bytes) -> FileInfo:
    dbx = get_client(access_token)
    meta = dbx.files_upload(content, path, mode=WriteMode.overwrite)
    return FileInfo(
        id=meta.id,
        name=meta.name,
        path=meta.path_display,
        size=meta.size,
        is_folder=False,
        modified=str(meta.server_modified),
    )


def delete_file(access_token: str, path: str) -> bool:
    dbx = get_client(access_token)
    dbx.files_delete_v2(path)
    return True


def rename_file(access_token: str, old_path: str, new_path: str) -> FileInfo:
    dbx = get_client(access_token)
    meta = dbx.files_move_v2(old_path, new_path).metadata
    return FileInfo(
        id=meta.id,
        name=meta.name,
        path=meta.path_display,
        size=getattr(meta, "size", None),
        is_folder=isinstance(meta, FolderMetadata),
        modified=str(meta.server_modified) if isinstance(meta, FileMetadata) else None,
    )
