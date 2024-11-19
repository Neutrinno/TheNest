from typing import Optional, Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.applications.database import get_async_session
from src.models import Application, RoommatePreference
from src.setting import settings

router = APIRouter(prefix = settings.application.prefix, tags=[settings.application.tags])


class ApplicationCreate(BaseModel):
    student_id: int
    full_name: str
    email: EmailStr
    admission_score: int = Field(gt=0, lt=100)
    preferred_student: EmailStr
    preferred_dormitory: Optional[Annotated[int, Field(ge=0)]]
    preferred_floor: Optional[Annotated[int, Field(ge=0)]]

class RoommateCreate(BaseModel):
    preferred_student: EmailStr

@router.post("/", response_model= ApplicationCreate)
async def create_application(new_application: ApplicationCreate,
                             new_roommate: RoommateCreate,
                             session: AsyncSession = Depends(get_async_session)):

    application = Application(**new_application.dict())
    session.add(application)
    await session.commit()
    await session.refresh(application)

    roommate_preferance = RoommatePreference(student_id = ApplicationCreate.student_id, **new_roommate.dict())

    session.add(roommate_preferance)
    await session.commit()
    await session.refresh(roommate_preferance)
    return {"message": "Your application has been successfully registered"}