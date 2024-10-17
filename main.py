from fastapi import FastAPI
from app.routers.campaign import router as campaign_router
from app.routers.recipient import router as recipient_router
from app.routers.notification import router as notification_router


app = FastAPI()


app.include_router(campaign_router, tags=['campaign'])
app.include_router(recipient_router, tags=['recipient'])
app.include_router(notification_router, tags=['notification'])
