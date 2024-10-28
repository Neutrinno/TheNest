from typing import Optional
from fastapi_users import schemas
from sqlalchemy.dialects.mssql import TIMESTAMP


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    email: str
    admission_score: int
    registered_at = TIMESTAMP
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True



class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    admission_score: int
    registered_at = TIMESTAMP
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
