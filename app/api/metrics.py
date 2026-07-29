from fastapi import APIRouter, Response, Depends
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.metrics import OPERATIONS_PENDING
from app.services.operation import count_waiting_operations

router = APIRouter()

@router.get("/metrics")
async def metrics(
        session: AsyncSession = Depends(get_session)
):

    pending = await count_waiting_operations(session)
    OPERATIONS_PENDING.set(pending)

    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )