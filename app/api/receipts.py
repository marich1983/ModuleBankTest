from fastapi import APIRouter, HTTPException, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.enums import OperationStatus
from app.schemas import ReceiptResponse
from app.services.operation import processing_status_to_done
from app.services.receipt import get_operation_by_receipt, check_provider_payment_id

router = APIRouter(
    prefix='/receipts',
    tags=['receipts']
)

@router.post(
    '/',
    status_code=201,
    summary='Получение call-back квитанций от провайдера'
)
async def get_receipt(
        receipt: ReceiptResponse,
        session: AsyncSession = Depends(get_session),
):
    async with session.begin():
        operation = await get_operation_by_receipt(
            session,
            receipt.operationId,
        )

        if operation is None:
            raise HTTPException(
                status_code=404,
                detail="Operation not found",
            )

        check_provider_payment_id(
            operation,
            receipt.providerPaymentId,
        )

        if receipt.result == "COMPLETED":
            if operation.status == OperationStatus.COMPLETED:
                return Response(status_code=204)

            await processing_status_to_done(
                session=session,
                operation=operation,
                receipt=receipt
            )

    return Response(status_code=201)