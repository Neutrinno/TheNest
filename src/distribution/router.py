from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import Result, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.distribution.database import get_async_session
from src.distribution.schemas import StudentList
from src.models import Application, StudentListing, Status

router = APIRouter()

"""
async def choose_room():
    pass

async def choose_floor():
    pass

async def choose_dormitory():
    pass
"""

async def status_update(session: AsyncSession):
    query = select(StudentListing).order_by(StudentListing.student_id)
    result: Result = await session.execute(query)
    student_list = result.scalars().all()

    for student in student_list:
        new_status = student.status

        status_query = select(Status).where(Status.student_id == student.student_id).limit(1)
        status_result = await session.execute(status_query)
        status_record = status_result.scalar_one_or_none()

        status_record.status = new_status

    await session.commit()

    return {"massage: Статусы успешно обновлены"}

"""
async def first_distribution(session: AsyncSession = Depends(get_async_session)):
    query = select(StudentListing)
    result: Result = await session.execute(query)
    student_list = result.scalars().all()

    for student in student_list:
        information = await session.execute(select(Application).where(Application.student_id == student.student_id).limit(1))
        if student.status == "Одоборено":
            if information.preferred_dormitory is not None:
                if information.floor is not None:
                    await choose_floor()
                pass
"""

@router.get("/", response_model=list[StudentList])
async def get_distribution(session: AsyncSession = Depends(get_async_session)):
    query = select(Application.id, Application.admission_score).order_by(desc(Application.admission_score))
    result = await session.execute(query)
    student_list = result.all()

    students_to_add = []
    for index, (id_, score) in enumerate(student_list):
        status = "Одобрено" if index < 80 else "В очереди"

        application_query = select(Application).where(Application.id == id_).limit(1)
        application_result = await session.execute(application_query)
        application = application_result.scalar_one_or_none()

        if application:
            wishes = any([
                application.preferred_dormitory is not None,
                application.preferred_floor is not None,
                application.first_preferred_student is not None,
                application.second_preferred_student is not None,
                application.third_preferred_student is not None,
            ])
            students_to_add.append(StudentListing(
                student_id=id_,
                admission_score=score,
                status=status,
                wishes=wishes
            ))

    session.add_all(students_to_add)
    await session.commit()
    await status_update(session)
    return [{"id": student[0], "admission_score": student[1]} for student in student_list]