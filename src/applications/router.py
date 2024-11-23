from datetime import datetime
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.applications.database import get_async_session
from src.applications.schemas import ApplicationCreate
from src.models import Application, Status

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

    application_id = application.id

    statement = Status(application_id=application_id,
                       student_id=application.student_id,
                       status="В обработке")

    session.add(statement)
    await session.commit()
    await session.refresh(statement)

    return {
        "message": f"Your application has been successfully registered. Number of application: {application_id}"
    }