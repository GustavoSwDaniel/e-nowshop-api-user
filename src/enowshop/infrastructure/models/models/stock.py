from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import func, event
from sqlalchemy.orm import relationship


from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data, generate_uuid


class Stock(Base):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    price = Column(Integer())
    saele = Column(Integer())
    quantity = Column(Integer())
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    product = relationship("Products", back_populates="stocks")

event.listen(Stock, 'before_insert', generate_data)
event.listen(Stock, 'before_insert', generate_uuid)
