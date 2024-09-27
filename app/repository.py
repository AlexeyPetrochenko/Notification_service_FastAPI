from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import CampaignOrm
from .schemes import CampaignAddSh, CampaignGetSh


def create_campaign(db: Session, campaign: CampaignAddSh) -> int:
    data_campaign = campaign.model_dump()
    db_campaign = CampaignOrm(**data_campaign)
    db.add(db_campaign)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Campaign name  already exists")
    db.refresh(db_campaign)
    return db_campaign.id


def get_campaign(db: Session, id: int) -> CampaignGetSh:
    query = select(CampaignOrm).where(CampaignOrm.id == id)
    campaign_model = db.scalars(query).first()
    if campaign_model is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignGetSh.from_orm(campaign_model)


def delete_campaign(db: Session, id: int) -> int:
    query = select(CampaignOrm).where(CampaignOrm.id == id)
    campaign_model = db.scalars(query).first()
    if campaign_model is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(campaign_model)
    db.commit()
    return id


def get_all_campaigns(db: Session) -> list[CampaignGetSh]:
    query = select(CampaignOrm)
    campaigns_models = db.scalars(query).all()
    campaigns = [CampaignGetSh.from_orm(campaign) for campaign in campaigns_models]
    return campaigns


def make_changes_in_campaign(db: Session, id: int, campaign_update: CampaignAddSh) -> CampaignGetSh:
    query = select(CampaignOrm).where(CampaignOrm.id == id)
    campaign_model = db.scalars(query).first()
    if campaign_model is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for field, new_value in campaign_update.model_dump().items():
        setattr(campaign_model, field, new_value)
    db.add(campaign_model)
    db.commit()
    db.refresh(campaign_model)
    return CampaignGetSh.from_orm(campaign_model)
