from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas import (
    OperationCreate,
    OperationResponse
)

from app.services.operation import create_operation, get_operation_by_operation_id

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

@router.get(
    "/{id}",
    response_model=OperationResponse,
    status_code=200,
)
async def get_operation_by_id(
    operation_id: str,
    session: AsyncSession = Depends(get_session),
):
    operation = await get_operation_by_operation_id(
        session=session,
        operation_id=operation_id,
    )

    if operation is None:
        raise HTTPException(
            status_code=404,
            detail="Operation not found",
        )

    return operation