import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.cognito import CurrentUser, get_current_user
from app.db.database import get_db
from app.db.models import ServiceTicketORM
from app.models.schemas import ServiceTicket, ServiceTicketCreate
from app.services.tickets import list_tickets_for_equipment, orm_to_schema

router = APIRouter(prefix="/tickets", tags=["Service Tickets"])


@router.post("", response_model=ServiceTicket)
async def create_ticket(
    body: ServiceTicketCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceTicket:
    row = ServiceTicketORM(
        id=str(uuid.uuid4()),
        equipment_id=body.equipment_id,
        title=body.title,
        description=body.description,
        priority=body.priority,
        status="open",
        error_codes=",".join(body.error_codes),
        created_by=user.name,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return orm_to_schema(row)


@router.get("/equipment/{equipment_id}", response_model=list[ServiceTicket])
async def get_equipment_tickets(
    equipment_id: str,
    user: CurrentUser = Depends(get_current_user),
) -> list[ServiceTicket]:
    _ = user
    return await list_tickets_for_equipment(equipment_id)
