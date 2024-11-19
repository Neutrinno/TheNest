from datetime import datetime
from typing import Optional, Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.applications.database import get_async_session
from src.models import Application, RoommatePreference
from src.setting import settings

router = APIRouter(prefix = settings.application.prefix, tags=[settings.application.tags])

class StudentId(BaseModel):
    student_id: int

class ApplicationCreate(StudentId):
    full_name: str
    admission_score: int = Field(gt=0, lt=101)
    preferred_dormitory: Optional[Annotated[int, Field(ge=0)]]
    preferred_floor: Optional[Annotated[int, Field(ge=0)]]

class RoommateCreate(StudentId):
    first_preferred_student: Optional[EmailStr] = None
    second_preferred_student: Optional[EmailStr] = None
    third_preferred_student: Optional[EmailStr] = None

@router.post("/")
async def create_application(new_application: ApplicationCreate,
                             new_roommate: RoommateCreate,
                             session: AsyncSession = Depends(get_async_session)):
    now = datetime.now()
    application = Application(**new_application.dict(),
                              submission_date=now)
    session.add(application)
    await session.commit()
    await session.refresh(application)

    if any(new_roommate.dict().values()):
        roommate_preference = RoommatePreference(**new_roommate.dict())
        session.add(roommate_preference)
        await session.commit()
        await session.refresh(roommate_preference)



    return {"message": "Your application has been successfully registered"}

