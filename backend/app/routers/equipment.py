from fastapi import APIRouter, Depends, HTTPException

from app.auth.cognito import CurrentUser, get_current_user
from app.models.schemas import Equipment, QRResolveRequest, QRResolveResponse
from app.services.equipment import equipment_service
from app.services.vector_store import vector_store
from app.services.tickets import list_tickets_for_equipment

router = APIRouter(prefix="/equipment", tags=["Equipment"])


@router.get("", response_model=list[Equipment])
async def list_equipment(user: CurrentUser = Depends(get_current_user)) -> list[Equipment]:
    _ = user
    return equipment_service.list_all()


@router.get("/{equipment_id}", response_model=Equipment)
async def get_equipment(
    equipment_id: str,
    user: CurrentUser = Depends(get_current_user),
) -> Equipment:
    _ = user
    eq = equipment_service.get(equipment_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return eq


@router.post("/qr/resolve", response_model=QRResolveResponse)
async def resolve_qr(
    body: QRResolveRequest,
    user: CurrentUser = Depends(get_current_user),
) -> QRResolveResponse:
    _ = user
    eq = equipment_service.resolve_qr(body.payload)
    if not eq:
        raise HTTPException(status_code=404, detail="Unknown QR code / asset")
    tickets = await list_tickets_for_equipment(eq.id)
    return QRResolveResponse(
        equipment=eq,
        recent_tickets=tickets[:5],
        document_count=vector_store.count(),
    )
