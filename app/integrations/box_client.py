"""Box integration using the Box Python SDK (box-sdk-gen v10+)."""
from __future__ import annotations

import io
from dataclasses import dataclass

from box_sdk_gen import (
    BoxClient,
    BoxOAuth,
    GetAuthorizeUrlOptions,
    OAuthConfig,
)
from box_sdk_gen.managers.uploads import (
    UploadFileAttributes,
    UploadFileAttributesParentField,
)

from app.config import API_URL, BOX_CLIENT_ID, BOX_CLIENT_SECRET


@dataclass
class FileInfo:
    id: str
    name: str
    size: int | None
    is_folder: bool
    modified: str | None


def _build_oauth(access_token: str = "", refresh_token: str = "") -> BoxOAuth:
    config = OAuthConfig(client_id=BOX_CLIENT_ID, client_secret=BOX_CLIENT_SECRET)
    oauth = BoxOAuth(config)
    # Manually inject tokens if we already have them
    if access_token:
        from box_sdk_gen.schemas.access_token import AccessToken

        oauth.token_storage.store(
            AccessToken(access_token=access_token, refresh_token=refresh_token)
        )
    return oauth


def get_auth_url() -> str:
    """Return the Box authorize URL."""
    oauth = _build_oauth()
    return oauth.get_authorize_url(
        options=GetAuthorizeUrlOptions(redirect_uri=f"{API_URL}/auth/box/callback")
    )


def exchange_code(code: str) -> tuple[str, str]:
    """Exchange auth code for (access_token, refresh_token)."""
    oauth = _build_oauth()
    token = oauth.get_tokens_authorization_code_grant(code)
    return token.access_token, token.refresh_token or ""


def get_client(access_token: str, refresh_token: str = "") -> BoxClient:
    oauth = _build_oauth(access_token, refresh_token)
    return BoxClient(oauth)


def list_files(access_token: str, folder_id: str = "0") -> list[FileInfo]:
    client = get_client(access_token)
    items = client.folders.get_folder_items(folder_id)
    files = []
    for entry in items.entries or []:
        is_folder = entry.type and entry.type.value == "folder"
        files.append(
            FileInfo(
                id=entry.id,
                name=getattr(entry, "name", "") or entry.id,
                size=getattr(entry, "size", None),
                is_folder=bool(is_folder),
                modified=str(getattr(entry, "modified_at", "")) or None,
            )
        )
    return files


def upload_file(access_token: str, folder_id: str, filename: str, content: bytes) -> FileInfo:
    client = get_client(access_token)
    attrs = UploadFileAttributes(
        name=filename,
        parent=UploadFileAttributesParentField(id=folder_id),
    )
    stream = io.BytesIO(content)
    result = client.uploads.upload_file(attrs, stream)
    uploaded = result.entries[0]
    return FileInfo(
        id=uploaded.id,
        name=uploaded.name,
        size=getattr(uploaded, "size", None),
        is_folder=False,
        modified=str(getattr(uploaded, "modified_at", "")) or None,
    )


def delete_file(access_token: str, file_id: str, is_folder: bool = False) -> bool:
    client = get_client(access_token)
    if is_folder:
        client.folders.delete_folder_by_id(file_id)
    else:
        client.files.delete_file_by_id(file_id)
    return True


def rename_file(
    access_token: str, file_id: str, new_name: str, is_folder: bool = False
) -> FileInfo:
    client = get_client(access_token)
    if is_folder:
        item = client.folders.update_folder_by_id(file_id, name=new_name)
    else:
        item = client.files.update_file_by_id(file_id, name=new_name)
    return FileInfo(
        id=item.id,
        name=item.name,
        size=getattr(item, "size", None),
        is_folder=is_folder,
        modified=str(getattr(item, "modified_at", "")) or None,
    )
