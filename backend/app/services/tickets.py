from datetime import datetime, timezone

from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import ServiceTicketORM
from app.models.schemas import ServiceTicket


def orm_to_schema(row: ServiceTicketORM) -> ServiceTicket:
    return ServiceTicket(
        id=row.id,
        equipment_id=row.equipment_id,
        title=row.title,
        description=row.description,
        priority=row.priority,
        status=row.status,
        error_codes=[c for c in row.error_codes.split(",") if c] if row.error_codes else [],
        created_by=row.created_by,
        created_at=row.created_at or datetime.now(timezone.utc),
    )


async def list_tickets_for_equipment(equipment_id: str) -> list[ServiceTicket]:
    async with SessionLocal() as db:
        result = await db.execute(
            select(ServiceTicketORM)
            .where(ServiceTicketORM.equipment_id == equipment_id)
            .order_by(ServiceTicketORM.created_at.desc())
        )
        return [orm_to_schema(r) for r in result.scalars().all()]
