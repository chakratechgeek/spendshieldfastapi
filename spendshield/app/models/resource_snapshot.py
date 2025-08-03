from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db import Base

class ResourceSnapshot(Base):
    __tablename__ = "resource_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now())
    resource_id = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=False, index=True)
    properties = Column(Text, nullable=True)  # JSON stored as text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
