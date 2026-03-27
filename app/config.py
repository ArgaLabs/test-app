from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# Dropbox
DROPBOX_APP_KEY = _get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = _get("DROPBOX_APP_SECRET")

# Box
BOX_CLIENT_ID = _get("BOX_CLIENT_ID")
BOX_CLIENT_SECRET = _get("BOX_CLIENT_SECRET")

# Google (Drive + Calendar)
GOOGLE_CLIENT_ID = _get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _get("GOOGLE_CLIENT_SECRET")

# Slack
SLACK_BOT_TOKEN = _get("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = _get("SLACK_CHANNEL_ID")

# Unstructured
UNSTRUCTURED_API_KEY = _get("UNSTRUCTURED_API_KEY")
UNSTRUCTURED_API_URL = _get("UNSTRUCTURED_API_URL", "https://api.unstructuredapp.io/general/v0/general")

# App
APP_SECRET_KEY = _get("APP_SECRET_KEY", "change-me")
FRONTEND_URL = _get("FRONTEND_URL", "http://localhost:3000")
API_URL = _get("API_URL", "http://localhost:8000")
