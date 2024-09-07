from datetime import datetime
from pydantic import BaseModel, Field, validator


class ReportSchema(BaseModel):
    id: int
    url: str
    created_at: datetime
    user_id: int

    class Config:
       orm_mode = True