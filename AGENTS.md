# AGENTS.md

## Cursor Cloud specific instructions

FieldTech Assistant is a split dev stack: **FastAPI backend** (`backend/`) and **Vite React PWA** (`frontend/`). Docker Compose (Chroma + MinIO) is optional; default dev uses in-process Chroma and local filesystem storage.

### Services (dev)

| Service | Port | Start |
|---------|------|--------|
| Backend | 8000 | `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000` |
| Frontend | 5173 | `cd frontend && npm run dev` |

Use **tmux** for long-running dev servers. The frontend proxies `/api` to `http://127.0.0.1:8000` (see `frontend/vite.config.ts`).

### First-time / VM notes

- On Debian/Ubuntu, `python3 -m venv` requires `python3.12-venv` (`apt install python3.12-venv`) before creating `backend/.venv`.
- Copy `backend/.env.example` → `backend/.env` once if missing (`AUTH_DEV_MODE=true` is enough for local dev).
- No `OPENAI_API_KEY` is required: pseudo-embeddings and template RAG answers still work for the E47 demo.

### Verify the stack

1. `curl -s http://127.0.0.1:8000/docs` → 200
2. `curl -s http://127.0.0.1:5173/` → 200
3. Hello-world flow: open http://localhost:5173 → **Ask** → **Try E47 demo** (or `POST /api/ask` with a dev token from `POST /api/auth/dev-token`).

### Lint / build (no dedicated test suite in repo)

- Frontend typecheck + production build: `cd frontend && npm run build` (`tsc --noEmit` + Vite).
- Backend: no pytest/ruff config; smoke-check with `cd backend && source .venv/bin/activate && python -c "from app.main import app"`.

### Optional infrastructure

`docker compose up -d` starts Chroma (`localhost:8001`) and MinIO (`9000`/`9001`). Not required for portfolio demo flows; backend falls back to ephemeral in-process Chroma when the HTTP client cannot reach Chroma.
