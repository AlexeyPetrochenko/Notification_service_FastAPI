from fastapi import FastAPI
from app.routers import router as campaign_router


app = FastAPI()


app.include_router(campaign_router)
