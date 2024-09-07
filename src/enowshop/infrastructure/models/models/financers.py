from sqlalchemy import Column, Integer, String, DateTime, Date,ForeignKey, Boolean, Numeric
from sqlalchemy import func, event
from sqlalchemy.orm import relationship

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data, generate_uuid


class Financers(Base):
    __tablename__ = 'financers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    is_recurrent = Column(Boolean, default=False)
    value = Column(Numeric(10, 2))
    type = Column(String(255))
    created_at = Column(DateTime)

event.listen(Financers, 'before_insert', generate_data)

