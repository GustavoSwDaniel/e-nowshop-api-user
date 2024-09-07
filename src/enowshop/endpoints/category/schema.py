from datetime import datetime

from pydantic import BaseModel, Field


class CreateCategorySchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=3, max_length=255)
    

class CategorySchema(BaseModel):
    uuid: str
    id: int
    name: str
    description: str
    image: str

    class Config:
        orm_mode = True
