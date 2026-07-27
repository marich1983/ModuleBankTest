from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.db.session import AsyncSession, get_session
from app.models import OperationOutbox, Operation

router = APIRouter(
    prefix='/debug_outbox'
)

@router.get(
    "/",
    status_code=200,
    summary='Получение outbox'
)
async def get_outbox(
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(
            Operation.operation_id,
            Operation.status.label("operation_status"),
            OperationOutbox.status.label("outbox_status"),
            OperationOutbox.retry_count,
            OperationOutbox.created_at,
        )
        .join(Operation)
        .order_by(OperationOutbox.created_at.desc())
    )

    result = await session.execute(stmt)

    return [
        {
            "operation_id": row.operation_id,
            "status_operation": row.operation_status,
            "status_outbox": row.outbox_status,
            "retry_count": row.retry_count,
            "created_at": row.created_at,
        }
        for row in result
    ]