# create schema with pydantic


from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StockSchema(BaseModel):
    id: str
    uuid: str
    product_id: str
    quantity: int
    uuid: str
    price: int

    class Config:
        orm_mode = True

class StockRegisterSchema(BaseModel):
    price: int
    quantity: int
    product_sku: str

class UpdateStock(BaseModel):
    price: Optional[int]
    quantity: Optional[int]
    product_id: Optional[int]
    physical_characteristics: Optional[dict]

class PaginateStockSchema(BaseModel):
    data: List[StockSchema]
    total: int
    offset: int
    count: int
    class Config:
        orm_mode = True

class StockUpdateSchema(BaseModel):
    price: int
    quantity: int
    class Config:
        orm_mode = True