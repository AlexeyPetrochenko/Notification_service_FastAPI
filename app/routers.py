from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .depends import get_db
from .schemes import CampaignAddSh, CampaignGetSh
from .repository import create_campaign, get_campaign, get_all_campaigns, delete_campaign, make_changes_in_campaign

router = APIRouter(prefix='/campaigns')


@router.post('')
def campaign_add(campaign: CampaignAddSh, db: Session = Depends(get_db)) -> dict[str, str]:
    new_campaign_id = create_campaign(db, campaign)
    return {'status': 'ok', 'message': f'Campaign - {new_campaign_id} added'}


@router.get('/list')
def campaigns_get(db: Session = Depends(get_db)) -> list[CampaignGetSh]:
    campaigns = get_all_campaigns(db)
    return campaigns


@router.get('/{campaign_id}')
def campaign_get(campaign_id: int, db: Session = Depends(get_db)) -> CampaignGetSh:
    campaign = get_campaign(db, campaign_id)
    return campaign


@router.put('/{campaign_id}')
def campaign_update(campaign_id: int, data_for_update: CampaignAddSh, db: Session = Depends(get_db)) -> CampaignGetSh:
    updated_campaign = make_changes_in_campaign(db, campaign_id, data_for_update) 
    return updated_campaign


@router.delete('/{campaign_id}')
def campaign_delete(campaign_id: int, campaign_update: CampaignAddSh, db: Session = Depends(get_db)) -> dict[str, str]:
    campaign_id = delete_campaign(db, campaign_id)
    return {'status': 'ok', 'massage': f'Campaign - {campaign_id} deleted'}

