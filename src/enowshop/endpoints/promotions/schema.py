from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, validator


class PromotionRegisterSchema(BaseModel):
    name: str
    discount: int
    expiration_date: datetime

    @validator('expiration_date')
    def expiration_date_must_be_in_the_future(cls, expiration_date):
        if expiration_date < datetime.now():
            raise ValueError('Expiration date must be in the future')

        if expiration_date > datetime.now() + timedelta(days=30):
            raise ValueError('Expiration date must be in the next 30 days')
        return expiration_date


class PromotionsSchema(BaseModel):
    uuid: str
    name: str
    discount: int
    expiration_date: datetime

    class Config:
        orm_mode = True


class PaginatePromotionsSchema(BaseModel):
    total: int
    offset: int
    count: int
    data: List[PromotionsSchema]


class UpdatePromotionSchema(BaseModel):
    name: Optional[str]
    discount: Optional[int]
    expiration_date: Optional[datetime]

    @validator('expiration_date')
    def expiration_date_must_be_in_the_future(cls, expiration_date):
        if expiration_date < datetime.now():
            raise ValueError('Expiration date must be in the future')

        if expiration_date > datetime.now() + timedelta(days=30):
            raise ValueError('Expiration date must be in the next 30 days')
        return expiration_date
