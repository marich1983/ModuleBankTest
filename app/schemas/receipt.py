from datetime import datetime

from pydantic import BaseModel

from app.enums import ReceiptResult


class ReceiptResponse(BaseModel):
    providerPaymentId: str
    operationId: str
    result: ReceiptResult
    message: str | None = None
    occurredAt: datetime
