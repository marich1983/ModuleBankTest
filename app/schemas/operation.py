from decimal import Decimal

from pydantic import BaseModel, Field
from app.enums import OperationStatus, OperationEventType, Currency


class OperationCreate(BaseModel):
    operationId: str = Field(alias="operation_id")
    amount: Decimal = Field(gt=0)
    currency: Currency
    description: str | None = None


class OperationResponse(BaseModel):
    operationId: str = Field(alias="operation_id")
    amount: Decimal
    currency: Currency
    description: str | None
    status: OperationStatus
    providerPaymentId: str | None = Field(
        alias="provider_payment_id"
    )

    class Config:
        from_attributes = True