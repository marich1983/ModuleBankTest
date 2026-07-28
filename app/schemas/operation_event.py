from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import OperationEventType, OperationStatus


class OperationEventResponse(BaseModel):
    eventId: int = Field(alias="sequence_number")

    type: OperationEventType

    fromStatus: OperationStatus | None = Field(
        alias="from_status"
    )

    toStatus: OperationStatus = Field(
        alias="to_status"
    )

    message: str

    occurredAt: datetime = Field(
        alias="created_at"
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )