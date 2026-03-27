# Test App — Unified File Manager

Manage files across **Dropbox**, **Box**, and **Google Drive** from a single interface. Parse documents with **Unstructured**. Manage **Google Calendar** events. Get **Slack** notifications on every file change.

## Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS 4

## Setup

### 1. Environment variables

```bash
cp .env.example .env
# Fill in your API keys and secrets
```

You'll need to create OAuth apps for:
- **Dropbox**: https://www.dropbox.com/developers/apps — set redirect URI to `http://localhost:8000/auth/dropbox/callback`
- **Box**: https://developer.box.com/ — set redirect URI to `http://localhost:8000/auth/box/callback`
- **Google**: https://console.cloud.google.com/apis/credentials — enable Drive API & Calendar API, set redirect URI to `http://localhost:8000/auth/google/callback`
- **Slack**: https://api.slack.com/apps — create a bot with `chat:write` scope, install to workspace
- **Unstructured**: https://unstructured.io/ — get an API key (or run locally)

### 2. Backend

```bash
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Features

- **File Management**: List, upload, delete, and rename files on Dropbox, Box, and Google Drive
- **Slack Notifications**: Automatic Slack messages on every file change (upload/delete/rename)
- **Document Parsing**: Upload any document (PDF, DOCX, PPTX, etc.) and parse it into structured elements via Unstructured
- **Calendar**: Create, edit, and delete Google Calendar events

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/auth/{provider}` | Start OAuth flow |
| GET | `/auth/{provider}/callback` | OAuth callback |
| GET | `/auth/status` | Which providers are connected |
| GET | `/files/{provider}` | List files |
| POST | `/files/{provider}/upload` | Upload a file |
| DELETE | `/files/{provider}` | Delete a file |
| PATCH | `/files/{provider}/rename` | Rename a file |
| GET | `/calendar/events` | List calendar events |
| POST | `/calendar/events` | Create event |
| PATCH | `/calendar/events/{id}` | Update event |
| DELETE | `/calendar/events/{id}` | Delete event |
| POST | `/documents/parse` | Parse a document |
| GET | `/health` | Health check |
