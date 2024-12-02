from datetime import datetime
from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Depends
from requests import request
from sqlalchemy import update, select, Result, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.applications.database import get_async_session
from src.applications.schemas import ApplicationCreate, StatusEnum
from src.distribution.schemas import StudentStatus
from src.models import Application, Status, Assignment, StudentListing, User
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory='src/templates')

@router.post("/create_application")
async def create_application(
    student_id: int = Form(...),
    first_name: str = Form(...),
    surname: str = Form(...),
    middle_name: str = Form(...),
    admission_score: int = Form(...),
    preferred_dormitory: int = Form(None),
    preferred_floor: int = Form(None),
    first_preferred_student: str = Form(None),
    second_preferred_student: str = Form(None),
    third_preferred_student: str = Form(None),
    session: AsyncSession = Depends(get_async_session)):

    now = datetime.now()

    application = Application(
        student_id=student_id,
        first_name=first_name,
        surname=surname,
        middle_name=middle_name,
        admission_score=admission_score,
        preferred_dormitory=preferred_dormitory,
        preferred_floor=preferred_floor,
        first_preferred_student=first_preferred_student,
        second_preferred_student=second_preferred_student,
        third_preferred_student=third_preferred_student,
        submission_date=now,
    )

    session.add(application)
    await session.commit()
    await session.refresh(application)

    application_id = application.id

    statement = Status(
        application_id=application_id,
        student_id=application.student_id,
        status="В обработке",
    )

    session.add(statement)
    await session.commit()
    await session.refresh(statement)

    return templates.TemplateResponse("success.html",
        {"request": request,
            "message": f"Ваша заявка успешно зарегистрирована. Номер заявки: {application_id}",
        }
    )

@router.get("/{student_id}", response_model=StudentStatus)
async def get_information(student_id: int, session: AsyncSession = Depends(get_async_session)):
    student_query = select(User).where(User.id == student_id)
    result: Result = await session.execute(student_query)
    student = result.scalar()

    print(f"Student data: {vars(student)}")
    status_query = select(Status).where(Status.student_id == student.id)
    result: Result = await session.execute(status_query)
    status = result.scalar_one_or_none()
    if not status:
        return StudentStatus(student_id=student.id,
                             email=student.email,
                             application_id=0,
                             status=StatusEnum.NotSubmitted)
    else:
        return StudentStatus(student_id=student.id,
                             email=student.email,
                             application_id=status.application_id,
                             status=status.status)

@router.delete("/delete_application/{student_id}")
async def delete_application(student_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        status_stmt = delete(Status).where(Status.student_id == student_id)
        await session.execute(status_stmt)

        application_stmt = delete(Application).where(Application.student_id == student_id)
        await session.execute(application_stmt)

        student_listing_query = select(StudentListing).where(StudentListing.student_id == student_id)
        student_listing = (await session.execute(student_listing_query)).scalar_one_or_none()

        if student_listing:
            student_listing_stmt = delete(StudentListing).where(StudentListing.student_id == student_id)
            await session.execute(student_listing_stmt)

        assignment_query = select(Assignment).where(Assignment.student_id == student_id)
        assignment = (await session.execute(assignment_query)).scalar_one_or_none()

        if assignment:
            assignment_stmt = delete(Assignment).where(Assignment.student_id == student_id)
            await session.execute(assignment_stmt)

        await session.commit()

        return {"message": "Заявка успешно удалена"}
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении заявки: {str(e)}")

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