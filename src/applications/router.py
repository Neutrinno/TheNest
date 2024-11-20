from datetime import datetime
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.applications.database import get_async_session
from src.applications.schemas import ApplicationCreate
from src.models import Application

router = APIRouter()


@router.post("/")
async def create_application(new_application: ApplicationCreate,
                             session: AsyncSession = Depends(get_async_session)):
    now = datetime.now()
    application = Application(**new_application.dict(),
                              submission_date=now)
    session.add(application)
    await session.commit()
    await session.refresh(application)

    query = select(Application).where(Application.student_id == application.student_id)
    result = await session.execute(query)
    application_id = result.scalars().first()

    return {"message": f"Your application has been successfully registered. Number of application: {application_id.id if application_id else 'not found'}"}



 #   if any(new_roommate.dict().values()):
 #       roommate_preference = RoommatePreference(**new_roommate.dict())
   #     session.add(roommate_preference)
    #    await session.commit()
    #    await session.refresh(roommate_preference)
