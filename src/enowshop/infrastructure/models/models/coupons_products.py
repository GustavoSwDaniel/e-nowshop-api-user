from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy import func, event
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, ENUM
from sqlalchemy.ext.mutable import MutableDict
from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data


class CouponsProducts(Base):
    __tablename__ = 'coupons_products'

    id = Column(Integer, primary_key=True)
    coupon_id = Column(Integer, ForeignKey('coupons.id'))
    product_id = Column(Integer, ForeignKey('products.id'))

    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

event.listen(CouponsProducts, 'before_insert', generate_data)
