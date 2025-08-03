from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.resource_snapshot import ResourceSnapshot
from app.schemas.resource_snapshot import ResourceSnapshotCreate, ResourceSnapshotRead

router = APIRouter()

@router.post("/resource-snapshots/", response_model=ResourceSnapshotRead)
def create_resource_snapshot(snapshot: ResourceSnapshotCreate, db: Session = Depends(get_db)):
    db_snapshot = ResourceSnapshot(**snapshot.dict())
    db.add(db_snapshot)
    try:
        db.commit()
        db.refresh(db_snapshot)
        return db_snapshot
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/resource-snapshots/", response_model=list[ResourceSnapshotRead])
def get_resource_snapshots(db: Session = Depends(get_db)):
    return db.query(ResourceSnapshot).all()
