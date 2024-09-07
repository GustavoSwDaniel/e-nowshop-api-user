# create sql tabel to cart emcommerce
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from enowshop.infrastructure.models.base import Base
import datetime
from sqlalchemy.orm import relationship

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expiration = Column(DateTime, default=datetime.datetime.utcnow)
    expired = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("Users")
    cart_items = relationship("CartItens", back_populates="cart")