from decimal import Decimal
from typing import List
from pydantic import BaseModel, validator


class CostRegister(BaseModel):
    name: str
    is_recurrent: bool = False
    value: float
    type: str

    class Config:
        orm_mode = True

class Costs(BaseModel):
    id: int
    name: str
    is_recurrent: bool = False
    value: Decimal
    type: str

    @validator('value')
    def value_to_decimal(cls, value):
        return f'{value}'

    class Config:
        orm_mode = True

class PaginateCostsSchema(BaseModel):
    total: int
    offset: int
    count: int
    data: List[Costs]
