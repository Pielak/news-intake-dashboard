from newsapi import NewsApiClient
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Article, Source, Trend, IngestionLog
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))

def collect_articles(db: Session, trend: Trend):
    try:
        newsapi = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))
        
        approved_sources = db.query(Source).filter(Source.status == "approved").all()
        approved_domains = [s.domain for s in approved_sources]
        
        if not approved_domains:
            return {"collected": 0, "reason": "Nenhuma fonte aprovada cadastrada"}

        from_date = (datetime.utcnow() - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S')
        
        response = newsapi.get_everything(
            q=trend.keyword_original,
            from_param=from_date,
            language='pt',
            sort_by='relevancy',
            page_size=10
        )

        collected = 0
        for item in response.get('articles', []):
            source_url = item.get('url', '')
            domain = source_url.split('/')[2] if '//' in source_url else ''
            domain = domain.replace('www.', '')

            if domain not in approved_domains:
                db.add(IngestionLog(
                    connector="newsapi",
                    item_type="article",
                    status="discarded",
                    reason=f"Domínio {domain} não está na allowlist"
                ))
                continue

            source = db.query(Source).filter(Source.domain == domain).first()
            
            existing = db.query(Article).filter(Article.url == item.get('url')).first()
            if existing:
                continue

            article = Article(
                trend_id=trend.id,
                source_id=source.id if source else None,
                title=item.get('title', ''),
                summary=item.get('description', ''),
                url=item.get('url', ''),
                canonical_url=item.get('url', ''),
                published_at=datetime.strptime(item['publishedAt'], '%Y-%m-%dT%H:%M:%SZ') if item.get('publishedAt') else None,
                relevance_score=1.0,
                final_score=1.0 * (source.priority_score if source else 1.0),
                language='pt',
                country='BR'
            )
            db.add(article)
            collected += 1

        db.commit()
        return {"collected": collected}

    except Exception as e:
        db.add(IngestionLog(
            connector="newsapi",
            item_type="article",
            status="error",
            reason=str(e)
        ))
        db.commit()
        raise e
