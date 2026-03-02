from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Article, Source, Trend

router = APIRouter()

@router.get("/")
def get_articles(trend_id: int = None, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Article, Source, Trend).join(
        Source, Article.source_id == Source.id, isouter=True
    ).join(
        Trend, Article.trend_id == Trend.id, isouter=True
    )
    
    if trend_id:
        query = query.filter(Article.trend_id == trend_id)
    
    results = query.order_by(Article.final_score.desc()).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "title": a.title,
            "summary": a.summary,
            "url": a.url,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "final_score": a.final_score,
            "source": {"name": s.name, "domain": s.domain} if s else None,
            "trend": {"keyword": t.keyword_display} if t else None
        }
        for a, s, t in results
    ]

@router.get("/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    result = db.query(Article, Source, Trend).join(
        Source, Article.source_id == Source.id, isouter=True
    ).join(
        Trend, Article.trend_id == Trend.id, isouter=True
    ).filter(Article.id == article_id).first()
    
    if not result:
        return {"error": "Artigo não encontrado"}
    
    a, s, t = result
    return {
        "id": a.id,
        "title": a.title,
        "summary": a.summary,
        "url": a.url,
        "published_at": a.published_at.isoformat() if a.published_at else None,
        "final_score": a.final_score,
        "source": {"name": s.name, "domain": s.domain} if s else None,
        "trend": {"keyword": t.keyword_display, "score": t.score} if t else None,
        "reason": f"Esta notícia foi exibida porque está relacionada à tendência '{t.keyword_display if t else ''}' e provém de uma fonte aprovada."
    }
