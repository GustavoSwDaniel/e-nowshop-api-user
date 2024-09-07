from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import func, event
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data, generate_sku


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    sku = Column(String(36))
    name = Column(String(255))
    description = Column(Text)
    image_url = Column(String(200))
    physical_characteristics = Column(MutableDict.as_mutable(JSON))
    is_active = Column(Boolean, default=True)
    brand = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    promotion_id = Column(Integer, ForeignKey('promotion.id'), nullable=True)
    category_products = relationship('CategoryProducts', back_populates='product')
    promotion = relationship('Promotion', back_populates='products')
    stocks = relationship("Stock", back_populates="product")
    recomendations = Column(MutableDict.as_mutable(JSON), nullable=True)

event.listen(Products, 'before_insert', generate_data)
event.listen(Products, 'before_insert', generate_sku)
