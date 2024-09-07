from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import func, event

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_uuid, generate_data

class Permissions(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    name = Column(String(50))
    description = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


