from datetime import datetime
from fastapi_users import schemas
from typing import Optional



class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    registered_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool]= False

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    email: str
    password: str
    registered_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False