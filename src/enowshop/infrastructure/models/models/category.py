from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy import func, event
from sqlalchemy.orm import relationship

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data, generate_uuid


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    name = Column(String(100))
    image = Column(String(255))
    description = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


event.listen(Category, 'before_insert', generate_uuid)
event.listen(Category, 'before_insert', generate_data)
