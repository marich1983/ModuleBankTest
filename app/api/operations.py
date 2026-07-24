from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas import (
    OperationCreate,
    OperationResponse
)

from app.services.operation import create_operation


router = APIRouter(
    prefix="/operations",
    tags=["operations"]
)


@router.post(
    "",
    response_model=OperationResponse,
    status_code=201
)
async def create(
    data: OperationCreate,
    session: AsyncSession = Depends(get_session)
):

    try:
        operation = await create_operation(
            session,
            data
        )

    except ValueError:
        raise HTTPException(
            status_code=409,
            detail="Operation already exists"
        )

    return operation