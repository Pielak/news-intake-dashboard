from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Trend
from app.services.trends_service import collect_trends, REGIONS

router = APIRouter()

@router.get("/")
def get_trends(region: str = "BR", db: Session = Depends(get_db)):
    trends = db.query(Trend).filter(
        Trend.region_code == region
    ).order_by(Trend.score.desc(), Trend.captured_at.desc()).limit(20).all()
    
    return [
        {
            "id": t.id,
            "keyword": t.keyword_display or t.keyword_ptbr or t.keyword_original,
            "score": t.score,
            "region_code": t.region_code,
            "region_name": t.region_name,
            "captured_at": t.captured_at.isoformat() if t.captured_at else None
        }
        for t in trends
    ]

@router.post("/collect")
def trigger_collect(region: str = "BR", db: Session = Depends(get_db)):
    result = collect_trends(db, region)
    return result

@router.get("/regions")
def get_regions():
    return [{"code": k, "name": v} for k, v in REGIONS.items()]
