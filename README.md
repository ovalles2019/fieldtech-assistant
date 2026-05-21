# FieldTech Assistant

A **RAG-powered field service assistant** for technicians who need fast answers from manuals, wiring diagrams, equipment guides, and service history — built for portfolios targeting infrastructure, AV, and manufacturing employers (M.C. Dean, Crestron, TI, Lockheed Martin, etc.).

## Demo question

> *"The HVAC controller is showing error code E47. What does it mean and what should I inspect?"*

Load asset `hvac-ctrl-001` (QR or Assets tab), tap **Try E47 demo** on the Ask screen.

## Features

| Feature | Implementation |
|--------|----------------|
| Equipment-specific retrieval | Chroma metadata filter on `equipment_id` |
| QR scan → asset context | `html5-qrcode` + `/api/equipment/qr/resolve` |
| Offline-first cache | IndexedDB (`idb-keyval`) + Workbox `NetworkFirst` for API |
| Service tickets | SQLite + REST `/api/tickets` |
| Technician feedback loop | Ratings stored in DB; positive feedback boosts chunk metadata |
| Document ingest | PDF/text/image OCR upload → chunk → embed → vector store |
| Auth | Cognito-ready JWT validation; **dev mode** issues local tokens |
| Storage | Local filesystem (default) or MinIO/S3-compatible bucket |

## Stack

- **Frontend:** React 18, Vite, PWA, mobile bottom nav
- **Backend:** FastAPI, ChromaDB, OpenAI (optional), boto3/MinIO
- **Infra:** Docker Compose (Chroma + MinIO)

## Quick start

### 1. Infrastructure (optional)

```bash
docker compose up -d
```

Chroma: `localhost:8001` · MinIO console: `localhost:9001`

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Optional: add OPENAI_API_KEY for GPT answers

uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### 4. Demo QR codes

```bash
pip install qrcode[pil]
python scripts/generate_qr.py
```

PNG files land in `frontend/public/qr/` — print or display for camera scan tests.

## Project structure

```
mySite/
├── backend/app/          # FastAPI, RAG, ingest, auth
├── frontend/src/         # React PWA UI
├── docker-compose.yml    # Chroma + MinIO
└── scripts/generate_qr.py
```

## Deploy live (Option A — single Docker container)

The repo includes a **multi-stage Dockerfile** that builds the React app and serves it from FastAPI on one port.

### Test locally with Docker

```bash
docker build -t fieldtech .
docker run -p 8000:8000 -e OPENAI_API_KEY= fieldtech
# Open http://localhost:8000
```

### Render (recommended)

1. Go to [render.com](https://render.com) → **New** → **Blueprint**
2. Connect GitHub repo `ovalles2019/fieldtech-assistant`
3. Render reads `render.yaml` and creates the web service
4. Add **Environment** variable `OPENAI_API_KEY` (optional, secret)
5. Deploy → open `https://fieldtech-assistant.onrender.com` (name may vary)

Or: **New Web Service** → Runtime **Docker** → point at this repo.

### Railway

1. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
2. Select the repo — Railway auto-detects `Dockerfile` / `railway.toml`
3. Add variable `OPENAI_API_KEY` if desired
4. **Settings** → generate domain

### Fly.io

```bash
fly launch    # uses fly.toml
fly secrets set OPENAI_API_KEY=sk-...
fly deploy
```

### Environment variables (production)

| Variable | Demo value | Notes |
|----------|------------|--------|
| `PORT` | `8000` | Set automatically on Render/Railway/Fly |
| `AUTH_DEV_MODE` | `true` | Set `false` + Cognito before public production |
| `OPENAI_API_KEY` | (secret) | Better RAG answers; works without it |
| `DEBUG` | `false` | |

On a single container, Chroma runs **in-memory** and re-seeds manuals on cold start (fine for portfolio demos). For persistent vectors, add a Chroma service later or use Chroma Cloud.

## License

MIT — portfolio / demonstration use.
