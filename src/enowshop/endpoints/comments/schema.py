from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator


class RegisterComment(BaseModel):
    product_id: int
    comment: Optional[str]
    rating: Optional[int]

class UserSchema(BaseModel):
    name: str
    
    class Config:
        orm_mode = True

class Comment(BaseModel):
    comment: str
    rating: int
    product_id: int
    user_id: int
    created_at: str
    user: UserSchema

    class Config:
        orm_mode = True

    @validator('created_at', pre=True)
    def convert_created_at(cls, value):
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        return value
    
class PaginateCommentsSchema(BaseModel):
    total: int
    offset: int
    count: int
    data: List[Comment]
    