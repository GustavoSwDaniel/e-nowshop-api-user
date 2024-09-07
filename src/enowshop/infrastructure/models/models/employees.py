from sqlalchemy import Column, Integer, String, DateTime, Date,ForeignKey
from sqlalchemy import func, event
from sqlalchemy.orm import relationship

from enowshop.infrastructure.models.base import Base
from enowshop.infrastructure.models.helpers.helpers import generate_data, generate_uuid


class Employees(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    name = Column(String(255))
    email = Column(String(100), unique=True)
    cpf = Column(String(11), unique=True)
    position = Column(String(100))
    salary = Column(Integer)
    password = Column(String(255))
    recovery_code = Column(String(255), nullable=True)
    admission_date = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    permission = Column(String(50))



event.listen(Employees, 'before_insert', generate_data)
event.listen(Employees, 'before_insert', generate_uuid)