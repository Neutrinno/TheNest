from datetime import datetime
from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Depends
from sqlalchemy import update, select, Result, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse

from src.applications.database import get_async_session
from src.applications.schemas import StatusEnum, ResultApplication
from src.distribution.schemas import StudentStatus
from src.models import Application, Status, Assignment, StudentListing, User, Bed, Room, Dormitory
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

    return RedirectResponse(url=f"/page/{student_id}", status_code=303)

@router.get("/{student_id}", response_model=StudentStatus)
async def get_information(student_id: int, session: AsyncSession = Depends(get_async_session)):
    student_query = select(User).where(User.id == student_id)
    result: Result = await session.execute(student_query)
    student = result.scalar()

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

@router.get("/result_application/{student_id}", response_model=ResultApplication)
async def get_result_application(student_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        status_query = select(Status).where(Status.student_id == student_id)
        result = await session.execute(status_query)
        status = result.scalar_one_or_none()

        if status.status in ["Ожидает очереди", "В ожидании", "Отклонено", "В обработке"]:
            return ResultApplication(student_id=student_id, status=status.status)

        assignment_query = select(Assignment).where(Assignment.student_id == student_id)
        result = await session.execute(assignment_query)
        assignment = result.scalar_one_or_none()

        bed_query = select(Bed).where(Bed.id == assignment.bed_id)
        result = await session.execute(bed_query)
        bed = result.scalar_one_or_none()

        room_query = select(Room).where(Room.id == bed.room_id)
        result = await session.execute(room_query)
        room = result.scalar_one_or_none()

        dormitory_query = select(Dormitory).where(Dormitory.id == room.dormitory_id)
        result = await session.execute(dormitory_query)
        dormitory = result.scalar_one_or_none()

        roommates_query = (select(Assignment.student_id)
                           .join(Bed, Bed.id == Assignment.bed_id)
                           .join(Room, Room.id == Bed.room_id)
                           .where(Room.id == room.id, Assignment.student_id != student_id))
        result = await session.execute(roommates_query)
        roommates_ids = result.scalars().all()

        roommates_data_query = (select(Application.first_name, Application.surname, Application.middle_name)
                                .where(Application.student_id.in_(roommates_ids)))
        result = await session.execute(roommates_data_query)
        roommates = result.all()

        roommates_info = [{"first_name": "", "surname": "", "middle_name": ""} for _ in range(3)]
        for i, roommate in enumerate(roommates[:3]):
            roommates_info[i] = {"first_name": roommate.first_name,
                                 "surname": roommate.surname,
                                 "middle_name": roommate.middle_name}

        return ResultApplication(student_id=student_id,
                                 status=status.status,
                                 dormitory_id=dormitory.id,
                                 address=dormitory.address,
                                 room_id=room.id,
                                 first_name=roommates_info[0]["first_name"],
                                 first_surname=roommates_info[0]["surname"],
                                 first_middle_name=roommates_info[0]["middle_name"],
                                 second_name=roommates_info[1]["first_name"],
                                 second_surname=roommates_info[1]["surname"],
                                 second_middle_name=roommates_info[1]["middle_name"],
                                 third_name=roommates_info[2]["first_name"],
                                 third_surname=roommates_info[2]["surname"],
                                 third_middle_name=roommates_info[2]["middle_name"])

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}")

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