import re
import uuid

from app.config import settings
from app.models.schemas import AskRequest, AskResponse, Citation, DocumentType, Equipment
from app.services.embeddings import embedding_service
from app.services.equipment import equipment_service
from app.services.vector_store import vector_store


ERROR_CODE_PATTERN = re.compile(r"\b([A-Z]\d{2,3})\b")


class RAGService:
    def ask(self, req: AskRequest) -> AskResponse:
        equipment: Equipment | None = None
        if req.equipment_id:
            equipment = equipment_service.get(req.equipment_id)

        doc_types = [DocumentType.manual, DocumentType.guide, DocumentType.wiring]
        if req.include_service_history:
            doc_types.append(DocumentType.service_history)

        citations = vector_store.search(
            query=req.question,
            equipment_id=req.equipment_id,
            doc_types=doc_types,
            top_k=6,
        )

        # Broaden search if equipment-filtered results are thin
        if len(citations) < 2 and req.equipment_id:
            global_hits = vector_store.search(query=req.question, equipment_id=None, doc_types=doc_types, top_k=4)
            seen = {c.document_id for c in citations}
            for hit in global_hits:
                if hit.document_id not in seen:
                    citations.append(hit)

        answer, inspections, confidence = self._generate_answer(req.question, citations, equipment)
        return AskResponse(
            answer=answer,
            citations=citations,
            equipment=equipment,
            suggested_inspections=inspections,
            confidence=confidence,
        )

    def _generate_answer(
        self,
        question: str,
        citations: list[Citation],
        equipment: Equipment | None,
    ) -> tuple[str, list[str], str]:
        context = "\n\n---\n\n".join(
            f"[{c.title} ({c.doc_type.value})]\n{c.excerpt}" for c in citations[:5]
        )
        error_codes = ERROR_CODE_PATTERN.findall(question)

        if settings.openai_api_key and embedding_service.openai and context:
            try:
                return self._llm_answer(question, context, equipment, error_codes)
            except Exception:
                pass

        return self._template_answer(question, citations, equipment, error_codes)

    def _llm_answer(
        self,
        question: str,
        context: str,
        equipment: Equipment | None,
        error_codes: list[str],
    ) -> tuple[str, list[str], str]:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        equip_line = f"Equipment: {equipment.name} ({equipment.model})" if equipment else "Equipment: not specified"
        codes = ", ".join(error_codes) if error_codes else "none detected"

        system = (
            "You are a senior field service engineer assistant. Answer concisely for technicians "
            "on site. Use only the provided context. List inspection steps as bullets. "
            "If context is insufficient, say what to verify manually."
        )
        user = f"{equip_line}\nError codes mentioned: {codes}\n\nQuestion: {question}\n\nContext:\n{context}"

        resp = client.chat.completions.create(
            model=settings.chat_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        text = resp.choices[0].message.content or ""
        inspections = _extract_bullets(text)
        return text, inspections, "high"

    def _template_answer(
        self,
        question: str,
        citations: list[Citation],
        equipment: Equipment | None,
        error_codes: list[str],
    ) -> tuple[str, list[str], str]:
        if not citations:
            return (
                "I could not find matching manual excerpts for this equipment. "
                "Verify the asset is linked and manuals are ingested, then retry.",
                ["Confirm QR/asset ID", "Check network and sync status"],
                "low",
            )

        top = citations[0]
        equip_name = equipment.name if equipment else "the selected asset"
        code_str = error_codes[0] if error_codes else "the reported condition"

        inspections: list[str] = []
        for c in citations:
            for line in c.excerpt.split("."):
                line = line.strip()
                if line.lower().startswith(("inspect", "verify", "check", "measure", "power cycle")):
                    inspections.append(line)
        if not inspections:
            inspections = [
                "Verify power and communication indicators on the unit",
                "Inspect terminal blocks and harnesses referenced in the manual",
                "Record findings and attach photos to the service ticket",
            ]

        answer = (
            f"For {equip_name}, documentation related to **{code_str}** indicates:\n\n"
            f"{top.excerpt}\n\n"
            f"Source: {top.title} ({top.doc_type.value}, relevance {top.score:.0%}).\n\n"
            "Follow the inspection sequence in the cited manual section before replacing components."
        )
        confidence = "high" if top.score > 0.5 else "medium"
        return answer, inspections[:6], confidence


def _extract_bullets(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•*").strip()
        if line and (line[0].isdigit() or line.lower().startswith(("verify", "check", "inspect"))):
            lines.append(line)
    return lines[:8]


rag_service = RAGService()
