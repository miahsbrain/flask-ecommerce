from project.extensions.dependencies import db
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime

# Base model
class BaseModel(db.Model):
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(tz=timezone.utc))