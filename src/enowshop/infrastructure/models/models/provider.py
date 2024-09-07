from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy import func, event
from sqlalchemy.orm import relationship

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data, generate_uuid


class Providers(Base):
    __tablename__ = 'providers'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    name = Column(String(100))
    email = Column(String(100))
    corporate_name = Column(String(14))
    phone = Column(String(12))
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())



event.listen(Providers, 'before_insert', generate_data)
event.listen(Providers, 'before_insert', generate_uuid)