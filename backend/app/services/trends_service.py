import feedparser
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Trend, IngestionLog

REGIONS = {
    "BR": "Brasil",
    "GLOBAL": "Mundo",
    "US": "Estados Unidos",
    "UK": "Reino Unido",
    "AU": "Australia",
    "JP": "Japao",
    "CA": "Canada",
}

RSS_FEEDS = {
    "BR": [
        ("Gazeta do Povo - Politica", "https://www.gazetadopovo.com.br/feed/politica/"),
        ("Gazeta do Povo - Economia", "https://www.gazetadopovo.com.br/feed/economia/"),
        ("Gazeta do Povo - Brasil", "https://www.gazetadopovo.com.br/feed/republica/"),
        ("Metropoles", "https://www.metropoles.com/feed"),
        ("CNN Brasil - Politica", "https://www.cnnbrasil.com.br/politica/feed/"),
        ("CNN Brasil - Economia", "https://www.cnnbrasil.com.br/economia/feed/"),
        ("CNN Brasil - Internacional", "https://www.cnnbrasil.com.br/internacional/feed/"),
        ("Revista Oeste", "https://revistaoeste.com/feed/"),
    ],
    "GLOBAL": [
        ("Reuters - Top News", "https://feeds.reuters.com/reuters/topNews"),
        ("Reuters - World", "https://feeds.reuters.com/Reuters/worldNews"),
    ],
    "US": [
        ("Reuters - US", "https://feeds.reuters.com/Reuters/domesticNews"),
    ],
}

def collect_trends(db: Session, region_code: str = "BR"):
    try:
        feeds = RSS_FEEDS.get(region_code, RSS_FEEDS.get("GLOBAL", []))

        # Titulos ja existentes para deduplicacao
        existing = set(
            t.keyword_original.strip().lower()
            for t in db.query(Trend.keyword_original).filter(Trend.region_code == region_code).all()
        )

        collected = 0
        seen_this_run = set()
        score_base = 20.0

        for feed_name, feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:8]:
                    title = entry.get('title', '').strip()
                    if not title:
                        continue

                    key = title.lower()
                    if key in existing or key in seen_this_run:
                        continue

                    seen_this_run.add(key)

                    trend = Trend(
                        keyword_original=title,
                        keyword_ptbr=title,
                        keyword_display=title,
                        score=round(score_base - (collected * 0.3), 2),
                        region_code=region_code,
                        region_name=REGIONS.get(region_code, region_code),
                        captured_at=datetime.utcnow(),
                        translation_status="ok"
                    )
                    db.add(trend)
                    collected += 1

            except Exception as feed_error:
                db.add(IngestionLog(
                    connector=f"rss:{feed_name}",
                    item_type="trend",
                    status="error",
                    reason=str(feed_error)
                ))

        db.commit()
        db.add(IngestionLog(
            connector="rss_feeds",
            item_type="trend",
            status="success",
            reason=f"{collected} tendencias novas coletadas para {region_code}"
        ))
        db.commit()
        return {"collected": collected, "region": region_code}

    except Exception as e:
        db.add(IngestionLog(
            connector="rss_feeds",
            item_type="trend",
            status="error",
            reason=str(e)
        ))
        db.commit()
        raise e
