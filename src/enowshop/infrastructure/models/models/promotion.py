from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey

from sqlalchemy import func, event
from sqlalchemy.orm import relationship

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data, generate_uuid


class Promotion(Base):
    __tablename__ = 'promotion'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    name = Column(String(255))
    discount = Column(Integer())
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expiration_date = Column(DateTime)

    products = relationship('Products')


event.listen(Promotion, 'before_insert', generate_data)
event.listen(Promotion, 'before_insert', generate_uuid)