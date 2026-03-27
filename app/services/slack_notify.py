"""Slack notification service — sends a message on every file change."""
from __future__ import annotations

import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID

logger = logging.getLogger(__name__)

_client: WebClient | None = None


def _get_client() -> WebClient | None:
    global _client
    if not SLACK_BOT_TOKEN:
        return None
    if _client is None:
        _client = WebClient(token=SLACK_BOT_TOKEN)
    return _client


def notify(action: str, provider: str, filename: str, details: str = "") -> bool:
    """Post a file-change notification to the configured Slack channel.

    Returns True if the message was sent successfully.
    """
    client = _get_client()
    if client is None or not SLACK_CHANNEL_ID:
        logger.warning("Slack not configured — skipping notification")
        return False

    emoji = {"upload": ":arrow_up:", "delete": ":wastebasket:", "rename": ":pencil2:"}.get(
        action, ":file_folder:"
    )

    text = f"{emoji} *{action.capitalize()}* on *{provider}*\n> `{filename}`"
    if details:
        text += f"\n> {details}"

    try:
        client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=text, mrkdwn=True)
        return True
    except SlackApiError as exc:
        logger.error("Slack notification failed: %s", exc.response["error"])
        return False
