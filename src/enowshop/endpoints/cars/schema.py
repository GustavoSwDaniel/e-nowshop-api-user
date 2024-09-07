from enowshop.endpoints.quotes.schema import QuotesListSchema
from enowshop.helpers import int_to_float
from pydantic import BaseModel, validator, root_validator
from typing import Dict, List, Optional
from datetime import datetime


class CarItems(BaseModel):
    product_uuid: str


class Item(BaseModel):
    quantity: int
    name: str
    value: int
    image_url: str
    product_uuid: str


class ChangeQuantity(BaseModel):
    quantity: int


class ProductsSchema(BaseModel):
    sku: str
    name: str
    description: str
    price: str
    image_url: str
    quantity_car: int
    brand: Optional[str]
    offer: Optional[str]

    class Config:
        orm_mode = True    
    

class CarSchema(BaseModel):
    user_uuid: str
    cart_total: str
    cart_total_term: str
    cash: str
    offer: str
    quoet_value: Optional[str]
    quoets: Optional[List[Dict]]
    items: List[ProductsSchema]
    chosen_quote: Optional[str]
    total_without_offer: Optional[str]
    