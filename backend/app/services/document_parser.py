import io
import re
from pathlib import Path

from pypdf import PdfReader

from app.models.schemas import DocumentType


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start = end - overlap if end < len(text) else end
    return chunks


def parse_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n\n".join(pages)


def parse_image_ocr(data: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract

        img = Image.open(io.BytesIO(data))
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def parse_file(path: Path, data: bytes | None = None) -> str:
    raw = data if data is not None else path.read_bytes()
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(raw)
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        ocr = parse_image_ocr(raw)
        return ocr if ocr.strip() else path.stem
    return raw.decode("utf-8", errors="ignore")


def build_chunk_metadata(
    document_id: str,
    title: str,
    doc_type: DocumentType,
    equipment_id: str | None,
    page: int | None,
    chunk_index: int,
) -> dict:
    meta: dict = {
        "document_id": document_id,
        "title": title,
        "doc_type": doc_type.value,
        "equipment_id": equipment_id or "global",
        "chunk_index": chunk_index,
    }
    if page is not None:
        meta["page"] = page
    return meta
