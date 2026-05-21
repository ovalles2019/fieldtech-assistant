from fastapi import APIRouter, Depends

from app.auth.cognito import CurrentUser, get_current_user
from app.models.schemas import AskRequest, AskResponse
from app.services.rag import rag_service

router = APIRouter(prefix="/ask", tags=["RAG"])


@router.post("", response_model=AskResponse)
async def ask_question(
    body: AskRequest,
    user: CurrentUser = Depends(get_current_user),
) -> AskResponse:
    _ = user
    return rag_service.ask(body)
