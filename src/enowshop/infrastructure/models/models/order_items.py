from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy import func, event
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, ENUM
from sqlalchemy.ext.mutable import MutableDict

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data, generate_uuid


class OrderItems(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    quantity = Column(Integer)
    unity_price = Column(Integer)
    total_price = Column(Integer)

    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Products')
    is_rated = Column(Boolean, default=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    teste = Column(String(36))
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())



event.listen(OrderItems, 'before_insert', generate_uuid)
event.listen(OrderItems, 'before_insert', generate_data)

