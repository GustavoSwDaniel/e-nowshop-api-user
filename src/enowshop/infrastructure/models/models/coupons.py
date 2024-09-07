from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy import func, event
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, ENUM
from sqlalchemy.ext.mutable import MutableDict
from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data


class Coupons(Base):
    __tablename__ = 'coupons'

    id = Column(Integer, primary_key=True)
    code = Column(String(255))
    total_available = Column(Integer)
    total_sold = Column(Integer)
    is_active = Column(Boolean, default=True)
    expiration_date = Column(Date)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

event.listen(Coupons, 'before_insert', generate_data)
