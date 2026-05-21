import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.cognito import CurrentUser, get_current_user
from app.db.database import get_db
from app.db.models import FeedbackORM
from app.models.schemas import FeedbackCreate, FeedbackResponse
from app.services.vector_store import vector_store

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    body: FeedbackCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    fid = str(uuid.uuid4())
    row = FeedbackORM(
        id=fid,
        query_id=body.query_id,
        question=body.question,
        answer=body.answer,
        rating=body.rating,
        equipment_id=body.equipment_id,
        comment=body.comment,
        citation_ids=",".join(body.citation_ids),
    )
    db.add(row)
    await db.commit()

    # Feedback loop: boost helpful chunks for future retrieval (demo: re-upsert with higher weight tag)
    if body.rating >= 4 and body.citation_ids:
        try:
            for cid in body.citation_ids[:3]:
                existing = vector_store.collection.get(ids=[cid], include=["documents", "metadatas"])
                if existing["ids"]:
                    meta = existing["metadatas"][0]
                    meta["feedback_boost"] = meta.get("feedback_boost", 0) + 1
                    vector_store.collection.update(ids=[cid], metadatas=[meta])
        except Exception:
            pass

    _ = user
    return FeedbackResponse(id=fid, message="Thank you — your feedback improves future answers.")
