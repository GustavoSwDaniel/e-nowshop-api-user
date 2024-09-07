import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy import func

from enowshop.infrastructure.models.base import Base


class State(enum.Enum):
    AC = 'Acre'
    AL = 'Alagoas'
    AP = 'Amapá'
    AM = 'Amazonas'
    BA = 'Bahia'
    CE = 'Ceará'
    DF = 'Distrito Federal'
    ES = 'Espírito Santo'
    GO = 'Goiás'
    MA = 'Maranhão'
    MT = 'Mato Grosso'
    MS = 'Mato Grosso do Sul'
    MG = 'Minas Gerais'
    PA = 'Pará'
    PB = 'Paraíba'
    PR = 'Paraná'
    PE = 'Pernambuco'
    PI = 'Piauí'
    RJ = 'Rio de Janeiro'
    RN = 'Rio Grande do Norte'
    RS = 'Rio Grande do Sul'
    RO = 'Rondônia'
    RR = 'Roraima'
    SC = 'Santa Catarina'
    SP = 'São Paulo'
    SE = 'Sergipe'
    TO = 'Tocantins'


class UserAddress(Base):
    __tablename__ = 'users_address'

    id = Column(Integer, primary_key=True)
    street = Column(String(100))
    cep = Column(String(15))
    city = Column(String(50))
    state = Column(Enum(State))
    village = Column(String(50))
    complement = Column(String(50), nullable=True)
    number = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    main = Column(Boolean , default=False)

    user_id = Column(Integer, ForeignKey('users.id'))
