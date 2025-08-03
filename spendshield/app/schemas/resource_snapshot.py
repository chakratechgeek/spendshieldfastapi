from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ResourceSnapshotBase(BaseModel):
    snapshot_time: Optional[datetime] = None
    resource_id: str
    resource_type: str
    properties: Optional[str] = None

class ResourceSnapshotCreate(ResourceSnapshotBase):
    pass

class ResourceSnapshotRead(ResourceSnapshotBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
