from sqlalchemy import Column, Enum, ForeignKey, Integer, String, DateTime, func, event

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data


class UsersPhones(Base):
    __tablename__ = 'users_phones'

    id = Column(Integer, primary_key=True)
    type = Column(Enum('Cell', 'Telephone', name='PhoneTypes'))
    number = Column(String(12))
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user_id = Column(Integer, ForeignKey('users.id'))


event.listen(UsersPhones, 'before_insert', generate_data)