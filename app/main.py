from fastapi import FastAPI

#  poetry run uvicorn app.main:app --reload
from app.api import health, metrics, operations, receipts
from app.core.logger import setup_logging

setup_logging()

app = FastAPI(
    title="Operation Payment Service - Test task for ModuleBank",
    version="1.0.0",
)


app.include_router(health.router)

app.include_router(operations.router)

app.include_router(receipts.router)

app.include_router(metrics.router)
