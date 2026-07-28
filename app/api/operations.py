from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas import OperationCreate, OperationResponse, OperationEventResponse

from app.services.operation import (
    create_operation,
    get_operation_by_operation_id,
    submit_operation_service,
)
from app.services.operation_event import get_operation_events

router = APIRouter(prefix="/operations", tags=["operations"])


@router.post(
    "", response_model=OperationResponse, status_code=201, summary="Создание операции"
)
async def create(data: OperationCreate, session: AsyncSession = Depends(get_session)):

    try:
        operation = await create_operation(session, data)

    except ValueError:
        raise HTTPException(status_code=409, detail="Operation already exists")

    return operation


# @router.get(
#     "/events",
#     # response_model=OperationResponse,
#     status_code=200,
# )
# async def get_events(
#     session: AsyncSession = Depends(get_session),
# ):
#
#     return await get_all_events(session=session)


@router.get(
    "/{id}/events",
    response_model=list[OperationEventResponse],
    status_code=200,
    summary="Получение всех событий по id операции",
)
async def get_events(
    id: str,
    session: AsyncSession = Depends(get_session),
):

    operation = await get_operation_by_operation_id(
        session=session,
        operation_id=id,
    )

    if operation is None:
        raise HTTPException(
            status_code=404,
            detail="Operation not found",
        )

    events = await get_operation_events(
        session=session,
        id=operation.id,
    )

    return events


@router.post(
    "/operations/{id}/submit",
    response_model=OperationResponse,
    summary="Подтверждение операции по id",
)
async def submit_operation(
    id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await submit_operation_service(
        session=session,
        operation_id=id,
    )

    response = OperationResponse.model_validate(result["operation"])

    return JSONResponse(
        status_code=result["status_code"], content=response.model_dump(mode="json")
    )


@router.get(
    "/{id}",
    response_model=OperationResponse,
    status_code=200,
    summary="Получение данных об операции по id",
)
async def get_operation_by_id(
    id: str,
    session: AsyncSession = Depends(get_session),
):
    operation = await get_operation_by_operation_id(
        session=session,
        operation_id=id,
    )

    if operation is None:
        raise HTTPException(
            status_code=404,
            detail="Operation not found",
        )

    return operation
