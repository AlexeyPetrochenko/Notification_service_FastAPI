from fastapi import FastAPI

from app.routers import router as compaign_router
from app.db import BaseOrm, sync_engine
from app.models import CampaignOrm


app = FastAPI()

app.include_router(compaign_router)


@app.on_event('startup')
def create_tables() -> None:
    BaseOrm.metadata.create_all(bind=sync_engine)
    print('База создана')
    
    
@app.on_event('shutdown')
def drop_tables() -> None:
    BaseOrm.metadata.drop_all(bind=sync_engine)
    print('База очищена')
