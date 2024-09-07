from enowshop.infrastructure.models.base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, event

from enowshop.infrastructure.models.helpers.helpers import generate_data


class UsersPasswordCodeRecovery(Base):
    __tablename__ = 'users_password_code_recovery'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    created_at = Column(DateTime)

    user_id = Column(Integer, ForeignKey('users.id'))


event.listen(UsersPasswordCodeRecovery, 'before_insert', generate_data)
