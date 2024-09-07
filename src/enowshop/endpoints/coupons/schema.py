from datetime import date
from pydantic import BaseModel
from typing import List

class GenerateCouponSchema(BaseModel):
    code: str


class CouponSchema(BaseModel):
    id: int
    code: str
    total_available: int
    total_sold: int
    expiration_date: date
    is_active: bool

    class Config:
        orm_mode = True

class RegisterCouponSchema(BaseModel):
    code: str
    total_available: int
    total_sold: int
    expiration_date: str
    products: List[str]