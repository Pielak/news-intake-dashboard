from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import trends, articles, sources, admin
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="News Intake Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trends.router, prefix="/api/trends", tags=["trends"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/api/health")
def health():
    return {"status": "ok"}
# teste webhook
