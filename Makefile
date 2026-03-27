.PHONY: api frontend install

install:
	uv sync
	cd frontend && npm install

api:
	uv run uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

dev:
	make api & make frontend

lint:
	uv run ruff check .
	uv run ruff format --check .

fix:
	uv run ruff check --fix .
	uv run ruff format .
