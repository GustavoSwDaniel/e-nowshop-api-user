from datetime import datetime, date
from enum import Enum
from typing import List

from pycpfcnpj import cpfcnpj
from pydantic import BaseModel, Field, validator, root_validator


class PhoneTypes(Enum):
    CELL = 'Cell'
    TELEPHONE = 'Telephone'


class PhonesSchema(BaseModel):
    type: PhoneTypes
    number: str

    class Config:
        use_enum_values = True


class ManageRegisterSchema(BaseModel):
    name: str
    email: str
    cpf: str
    position: str
    salary: int
    password: str = Field(regex='^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}')
    permission: str

    @validator('cpf')
    def cpf_validate(cls, data):
        if not cpfcnpj.validate(data):
            raise ValueError('Invalid CPF')

        return data

    @validator('name')
    def capitalize_name(cls, data: str):
        data = data.capitalize()
        return data


class ManagerLoginSchema(BaseModel):
    username: str
    password: str


class ManagerLoginResponseSchema(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    name: str
    last_name: str
    email: str
    uuid: str


class PhonesResponseSchema(PhonesSchema):
    class Config:
        orm_mode = True
        use_enum_values = True


class EmployeesDataSchema(BaseModel):
    uuid: str
    name: str
    last_name: str
    email: str
    cpf: str
    position: str
    admission_date: datetime
    created_at: datetime
    employees_phones: List[PhonesResponseSchema]

    class Config:
        orm_mode = True
        use_enum_values = True


class EmployeesDataListSchema(BaseModel):
    uuid: str
    name: str
    email: str
    cpf: str
    position: str
    admission_date: datetime
    created_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


class PaginateEmployeeListSchema(BaseModel):
    total: int
    offset: int
    count: int
    data: List[EmployeesDataListSchema]
