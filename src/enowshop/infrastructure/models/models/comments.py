from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy import func, event
from sqlalchemy.orm import relationship

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data, generate_uuid


class Comments(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    comment = Column(String, nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Users")
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime)


event.listen(Comments, 'before_insert', generate_data)
