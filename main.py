from fastapi import FastAPI
from typing import Any
from contextlib import asynccontextmanager
from app.routers import router as campaign_router
from app.db import create_tables, delete_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    await create_tables()
    print("База готова")
    yield
    await delete_tables()
    print("База очищена")

app = FastAPI(lifespan=lifespan)


app.include_router(campaign_router)
