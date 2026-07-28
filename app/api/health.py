from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", status_code=200)
async def health_check():
    return {"status": "ok"}
