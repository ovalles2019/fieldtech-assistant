from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.database import init_db
from app.models.schemas import DocumentType, HealthResponse
from app.routers import ask, auth, documents, equipment, feedback, tickets
from app.services.ingest import ingest_service
from app.services.storage import storage_service
from app.services.vector_store import vector_store


def seed_knowledge_base() -> None:
    if vector_store.count() > 0:
        return

    data_dir = Path(__file__).resolve().parent / "data" / "manuals"
    seeds = [
        ("hvac_e47_troubleshooting.txt", "Carrier Infinity — Error E47 Diagnostics", DocumentType.manual, "hvac-ctrl-001"),
        ("crestron_cp4_wiring.txt", "Crestron CP4-R Wiring Guide", DocumentType.wiring, "crestron-av-042"),
        ("ups_eaton_service.txt", "Eaton 9PX Service History", DocumentType.service_history, "ups-ti-008"),
    ]
    for filename, title, doc_type, equipment_id in seeds:
        path = data_dir / filename
        if path.exists():
            ingest_service.ingest_file_path(path, title, doc_type, equipment_id)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    vector_store.connect()
    seed_knowledge_base()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(ask.router, prefix="/api")
app.include_router(equipment.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(documents.router, prefix="/api")


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        chroma=vector_store.health_check(),
        storage=storage_service.health_check(),
        auth_mode="dev" if settings.auth_dev_mode else "cognito",
    )


FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
