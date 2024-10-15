from fastapi import FastAPI
from app.routers.campaign import router as campaign_router
from app.routers.recipient import router as recipient_router


app = FastAPI()


app.include_router(campaign_router)
app.include_router(recipient_router)
