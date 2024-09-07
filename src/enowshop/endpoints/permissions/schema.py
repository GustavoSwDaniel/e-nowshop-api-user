from datetime import datetime
from pydantic import BaseModel, Field, validator


class PermissionSchema(BaseModel):
    name: str = Field(..., title='Permission name', max_length=100)
    description: str = Field(..., title='Permission description', max_length=200)

class PermissionResponseSchema(BaseModel):
    id: int
    uuid: str
    name: str
    description: str

    class Config:
        orm_mode = True