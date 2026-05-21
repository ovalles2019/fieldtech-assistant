from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    manual = "manual"
    wiring = "wiring"
    guide = "guide"
    service_history = "service_history"


class Equipment(BaseModel):
    id: str
    asset_tag: str
    name: str
    manufacturer: str
    model: str
    location: str
    install_date: str | None = None
    qr_payload: str


class DocumentMeta(BaseModel):
    id: str
    equipment_id: str | None
    title: str
    doc_type: DocumentType
    s3_key: str
    page_count: int | None = None


class Citation(BaseModel):
    document_id: str
    title: str
    doc_type: DocumentType
    excerpt: str
    page: int | None = None
    score: float


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    equipment_id: str | None = None
    include_service_history: bool = True


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    equipment: Equipment | None = None
    suggested_inspections: list[str] = []
    confidence: str = "medium"


class QRResolveRequest(BaseModel):
    payload: str


class QRResolveResponse(BaseModel):
    equipment: Equipment
    recent_tickets: list["ServiceTicket"] = []
    document_count: int = 0


class ServiceTicketCreate(BaseModel):
    equipment_id: str
    title: str
    description: str
    priority: str = "medium"
    error_codes: list[str] = []


class ServiceTicket(BaseModel):
    id: str
    equipment_id: str
    title: str
    description: str
    priority: str
    status: str
    error_codes: list[str]
    created_by: str
    created_at: datetime


class FeedbackCreate(BaseModel):
    query_id: str | None = None
    question: str
    answer: str
    rating: int = Field(..., ge=1, le=5)
    equipment_id: str | None = None
    comment: str | None = None
    citation_ids: list[str] = []


class FeedbackResponse(BaseModel):
    id: str
    message: str


class IngestRequest(BaseModel):
    equipment_id: str | None = None
    title: str
    doc_type: DocumentType


class HealthResponse(BaseModel):
    status: str
    chroma: bool
    storage: bool
    auth_mode: str
