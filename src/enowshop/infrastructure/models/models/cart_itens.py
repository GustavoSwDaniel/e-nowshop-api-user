from sqlalchemy import Column, Integer, ForeignKey, DateTime
from enowshop.infrastructure.models.base import Base
import datetime
from sqlalchemy.orm import relationship

class CartItens(Base):
    __tablename__ = "carts_itens"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=0)

    cart = relationship("Cart", back_populates="cart_items")
    products = relationship('Products', backref="products")

