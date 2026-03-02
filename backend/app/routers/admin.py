from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Trend, Article, Source, IngestionLog
from app.services.trends_service import collect_trends
from app.services.news_service import collect_articles

router = APIRouter()

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    total_trends = db.query(Trend).count()
    total_articles = db.query(Article).count()
    total_sources = db.query(Source).filter(Source.status == "approved").count()
    total_logs = db.query(IngestionLog).count()
    last_log = db.query(IngestionLog).order_by(IngestionLog.created_at.desc()).first()
    
    return {
        "total_trends": total_trends,
        "total_articles": total_articles,
        "approved_sources": total_sources,
        "total_logs": total_logs,
        "last_collection": last_log.created_at.isoformat() if last_log else None
    }

@router.post("/collect-now")
def collect_now(region: str = "BR", db: Session = Depends(get_db)):
    trends_result = collect_trends(db, region)
    
    trends = db.query(Trend).filter(Trend.region_code == region).order_by(
        Trend.captured_at.desc()
    ).limit(5).all()
    
    articles_collected = 0
    for trend in trends:
        try:
            result = collect_articles(db, trend)
            articles_collected += result.get("collected", 0)
        except:
            pass
    
    return {
        "trends_collected": trends_result.get("collected", 0),
        "articles_collected": articles_collected,
        "region": region
    }

@router.get("/logs")
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(IngestionLog).order_by(
        IngestionLog.created_at.desc()
    ).limit(limit).all()
    return [
        {
            "id": l.id,
            "connector": l.connector,
            "item_type": l.item_type,
            "status": l.status,
            "reason": l.reason,
            "created_at": l.created_at.isoformat() if l.created_at else None
        }
        for l in logs
    ]

@router.post("/sources/{source_id}/approve")
def approve_source(source_id: int, db: Session = Depends(get_db)):
    s = db.query(Source).filter(Source.id == source_id).first()
    if not s:
        return {"error": "Fonte não encontrada"}
    s.status = "approved"
    db.commit()
    return {"id": s.id, "status": s.status}

@router.post("/sources/{source_id}/block")
def block_source(source_id: int, db: Session = Depends(get_db)):
    s = db.query(Source).filter(Source.id == source_id).first()
    if not s:
        return {"error": "Fonte não encontrada"}
    s.status = "blocked"
    db.commit()
    return {"id": s.id, "status": s.status}
