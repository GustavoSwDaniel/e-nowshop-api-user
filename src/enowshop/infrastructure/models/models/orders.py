from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy import func, event
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, ENUM
from sqlalchemy.ext.mutable import MutableDict
from enowshop.infrastructure.models.base import Base


from enowshop.infrastructure.models.helpers.helpers import generate_data

class Orders(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    total_amount = Column(Integer())
    purchase_amount = Column(Integer())
    shipping_amount = Column(Integer())
    installments = Column(Integer, nullable=True)
    payment_method = Column(ENUM('credit_card', 'pix', 'boleto', name='payment_methods_enum'))
    meta_data = Column(MutableDict.as_mutable(JSON))
    send_infos = Column(MutableDict.as_mutable(JSON))
    send_type_id = Column(Integer)
    status = Column(ENUM('approved', 'pending', 'denied', 'canceled', 'refunded', name='status_enum'), default='pending')
    status_send = Column(ENUM('pending', 'sent', 'delivered', 'canceled', name='status_send_enum'), default='pending')
    link_label_print = Column(String(), nullable=True)
    payment_date = Column(DateTime, nullable=True)
    payment_id = Column(String(), nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user_id = Column(Integer, ForeignKey('users.id'))
    address_id = Column(Integer, ForeignKey('users_address.id'))
    address = relationship('UserAddress')
    order_items = relationship('OrderItems')
    


event.listen(Orders, 'before_insert', generate_data)
