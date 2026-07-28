from datetime import datetime
from typing import Literal

from pydantic import BaseModel
from app.enums import ReceiptResult


class ReceiptResponse(BaseModel):
    providerPaymentId: str
    operationId: str
    result: ReceiptResult
    message: str | None = None
    occurredAt: datetime