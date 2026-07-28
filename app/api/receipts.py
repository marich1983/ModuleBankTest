from fastapi import APIRouter, HTTPException, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.enums import OperationStatus, OperationEventType
from app.schemas import ReceiptResponse
from app.services.operation import processing_status_to_done
from app.services.operation_event import add_operation_event
from app.services.receipt import get_operation_by_receipt, check_provider_payment_id, receipt_processing

router = APIRouter(
    prefix='/receipts',
    tags=['receipts']
)

@router.post(
    '/',
    status_code=201,
    summary='Получение call-back квитанций от провайдера'
)
async def get_callback_receipt(
        receipt: ReceiptResponse,
        session: AsyncSession = Depends(get_session),
):
    async with session.begin():
        status_code = await receipt_processing(
            session=session,
            receipt=receipt
        )

    return Response(status_code=status_code)