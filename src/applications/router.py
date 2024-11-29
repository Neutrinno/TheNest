from datetime import datetime
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from src.applications.database import get_async_session
from src.applications.schemas import ApplicationCreate
from src.distribution.schemas import StudentStatus
from src.models import Application, Status, Assignment, StudentListing

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

    return {"message": f"Your application has been successfully registered. Number of application: {application_id}"}

@router.get("/{student_id}", response_model=StudentStatus)
async def get_information(student_id: int, session: AsyncSession = Depends(get_async_session)):
    return await session.get(Status, student_id)

@router.put("/get_confirmation/{student_id}", response_model=str)
async def get_confirmation(student_id: int, session: AsyncSession = Depends(get_async_session)):
    assignment_stmt = update(Assignment).where(Assignment.student_id == student_id).values(application_status = "Подтвержден")
    await session.execute(assignment_stmt)

    student_listing_stmt = update(StudentListing).where(StudentListing.student_id == student_id).values(status="Подтвержден")
    await session.execute(student_listing_stmt)

    status_stmt = update(Status).where(Status.student_id == student_id).values(status = "Подтвержден")
    await session.execute(status_stmt)
    await session.commit()

    return "Подтверждение получено"