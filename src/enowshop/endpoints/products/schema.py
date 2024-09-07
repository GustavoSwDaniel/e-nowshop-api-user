from typing import List, Optional, Dict

from pydantic import BaseModel, Field, validator

from enowshop.endpoints.helpers import int_to_float
from datetime import datetime


class CategorySchema(BaseModel):
    name: str
    uuid: str

    class Config:
        orm_mode = True


class CreateProductSchema(BaseModel):
    category: CategorySchema

    class Config:
        orm_mode = True

class StockSchema(BaseModel):
    quantity: int
    price: float

    class Config:
        orm_mode = True


class CreateProductReponseSchema(BaseModel):
    name: str
    sku: str
    description: str
    brand: str = None
    image_url: str
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

class ProductsSchema(BaseModel):
    name: str
    sku: str
    id: int
    description: str
    brand: str = None
    image_url: str
    created_at: datetime
    price: Optional[float]
    is_active: bool
    category: List[CategorySchema]
    stocks: Optional[List[StockSchema]]
    recomendations_products: Optional[List]

    class Config:
        orm_mode = True


class PaginateProductsSchema(BaseModel):
    total: int
    offset: int
    count: int
    data: List[ProductsSchema]

class DimensionSchema(BaseModel):
    width: float
    height: float
    depth: float
    weight: float
class ProductsInfoSchema(BaseModel):
    description: str
    characteristics: List[Dict]
    technical_specifications: List[Dict]
    dimensions: DimensionSchema

class PhysicalCharacteristicsSchema(BaseModel):
    Height: float
    Width: float
    Length: float
    Weight: float

class ProductRegisterSchema(BaseModel):
    name: str
    description: str
    image_url: str
    brand: str = None
    category_uuid: str
    physical_characteristics: PhysicalCharacteristicsSchema
    



class UpdateProductSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    image_url: Optional[str]
    is_active: Optional[bool]


class ProductsWithDiscountSchema(ProductsSchema):
    new_price: int

    class Config:
        orm_mode = True


class PaginateProductsWithPromotionsSchema(PaginateProductsSchema):
    data: List[ProductsWithDiscountSchema]