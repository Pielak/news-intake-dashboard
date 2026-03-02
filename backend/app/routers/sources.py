from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Source
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class SourceCreate(BaseModel):
    name: str
    domain: str
    status: str = "approved"
    priority_score: float = 1.0
    editorial_label: Optional[str] = None
    notes: Optional[str] = None

@router.get("/")
def get_sources(status: str = None, db: Session = Depends(get_db)):
    query = db.query(Source)
    if status:
        query = query.filter(Source.status == status)
    sources = query.order_by(Source.priority_score.desc()).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "domain": s.domain,
            "status": s.status,
            "priority_score": s.priority_score,
            "editorial_label": s.editorial_label,
            "notes": s.notes,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in sources
    ]

@router.post("/")
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    existing = db.query(Source).filter(Source.domain == source.domain).first()
    if existing:
        return {"error": "Domínio já cadastrado"}
    new_source = Source(**source.dict())
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return {"id": new_source.id, "domain": new_source.domain, "status": new_source.status}

@router.put("/{source_id}")
def update_source(source_id: int, source: SourceCreate, db: Session = Depends(get_db)):
    s = db.query(Source).filter(Source.id == source_id).first()
    if not s:
        return {"error": "Fonte não encontrada"}
    for key, value in source.dict().items():
        setattr(s, key, value)
    db.commit()
    return {"id": s.id, "status": s.status}

@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    s = db.query(Source).filter(Source.id == source_id).first()
    if not s:
        return {"error": "Fonte não encontrada"}
    db.delete(s)
    db.commit()
    return {"deleted": source_id}
