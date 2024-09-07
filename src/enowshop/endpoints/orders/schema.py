import datetime
import enum
from typing import Dict, List, Optional, Union
from enowshop.infrastructure.models.models.users_address import State

from pydantic import BaseModel, Field, validator


class PaymentMethod(enum.Enum):
    CREDIT_CART = 'card'
    BOLETO = 'billet'
    PIX = 'pix'


class AddressSchema(BaseModel):
    street: str
    cep: str
    city: str
    state: State
    village: str
    number: int
    complement: Union[str, None]

    class Config:
        orm_mode = True
        use_enum_values = True

class ProductSchema(BaseModel):
    name: str
    image_url: str
    id: int

    class Config:
       orm_mode = True


class OrderItemsReponseSchema(BaseModel):
    uuid: str
    quantity: int
    product: ProductSchema
    is_rated: bool

    class Config:
       orm_mode = True

class OrderItemsSchema(BaseModel):
    uuid: str
    quantity: int
    

class DownloadBillet(BaseModel):
    url: str

class CreateOrderSchema(BaseModel):
    address_id: int
    quote_type_id: int
    quote_type: str
    quote_value: float
    purchase_amount: float
    total_value: float
    card_info: Optional[Dict]
    payment_method: PaymentMethod = Field(alias="paymentMethod")
    items: List[OrderItemsSchema]

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True 


class PaymentInfoSchema(BaseModel):
    billingType: str
    value: float

    # pix
    encodedImage: Optional[str]
    code: Optional[str]

    # card
    card_holder_info: Optional[Dict]
    status: Optional[str]

    # billet
    billet_url: Optional[str]
    bar_code: Optional[str]
    identification_field: Optional[str]

class OrderCreatedSchema(BaseModel):
    uuid: str
    payment_info: PaymentInfoSchema



class ItensSchema(BaseModel):
    uuid: str

class CalcSchema(BaseModel):
    address_uuid: str
    items: List[OrderItemsSchema]


class UpdateStatusSchema(BaseModel):
    status: str

class UpdateStatusSendoSchema(BaseModel):
    status_send: str

class OrderReponse(BaseModel):
    uuid: str
    total_amount: int
    status: str
    payment_method: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    address: AddressSchema
    order_items: List[OrderItemsReponseSchema]

    class Config:
        orm_mode = True

    @validator('total_amount')
    def convert_total_amount(cls, v):
        return f'{v/100:.2f}'


class OrderSchema(BaseModel):
    id: int
    uuid: Optional[str]
    total_amount: Optional[int]
    status: Optional[str]
    payment_method: Optional[str]
    status_send: Optional[str]
    created_at: datetime.datetime
    link_label_print: Optional[str]
    order_items: List[OrderItemsReponseSchema]

    class Config:
        orm_mode = True

    @validator('total_amount')
    def convert_total_amount(cls, v):
        return f'{v/100:.2f}'

    @validator('created_at')
    def convert_created_at(cls, v):
        return v.strftime('%Y-%m-%d')


class OrdersPaginateSchema(BaseModel):
    total: int
    offset: int
    count: int
    data: List[OrderSchema]