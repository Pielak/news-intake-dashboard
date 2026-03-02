from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    domain = Column(String(200), unique=True, nullable=False)
    status = Column(String(20), default="approved")
    priority_score = Column(Float, default=1.0)
    editorial_label = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Trend(Base):
    __tablename__ = "trends"
    id = Column(Integer, primary_key=True)
    keyword_original = Column(String(500), nullable=False)
    keyword_ptbr = Column(String(500))
    keyword_display = Column(String(500))
    score = Column(Float)
    region_code = Column(String(10))
    region_name = Column(String(100))
    captured_at = Column(DateTime, default=datetime.utcnow)
    translation_status = Column(String(20), default="pending")
    category_id = Column(Integer, ForeignKey("categories.id"))
    articles = relationship("Article", back_populates="trend")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    trend_id = Column(Integer, ForeignKey("trends.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    url = Column(String(1000), unique=True)
    canonical_url = Column(String(1000))
    published_at = Column(DateTime)
    relevance_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)
    language = Column(String(10))
    country = Column(String(10))
    trend = relationship("Trend", back_populates="articles")
    source = relationship("Source")

class IngestionLog(Base):
    __tablename__ = "ingestion_logs"
    id = Column(Integer, primary_key=True)
    connector = Column(String(100))
    item_type = Column(String(50))
    status = Column(String(20))
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
