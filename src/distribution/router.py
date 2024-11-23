from importlib.metadata import distribution

from fastapi import APIRouter
from fastapi.params import Depends
from pygments.lexer import default
from sqlalchemy import Result, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.distribution.database import get_async_session
from src.distribution.schemas import StudentList
from src.models import Application, StudentListing, Status

router = APIRouter()


async def choose_room():
    pass

async def choose_floor():
    pass

async def choose_dormitory():
    pass


async def status_update(session: AsyncSession = Depends(get_async_session)):
    query = select(StudentListing).order_by(StudentListing.student_id)
    result: Result = await session.execute(query)
    student_list = result.scalars().all()

    for student in student_list:
        new_status = student.status

        status_record = await session.execute(select(Status.student_id == student.id).limit(1))
        status_record.status = new_status

    await session.commit()
    return {"massage: Статусы успешно обновлены"}


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


@router.get("/", response_model=list[StudentList])
async def get_distribution(session: AsyncSession = Depends(get_async_session)):

    query = select(Application.id, Application.admission_score).order_by(desc(Application.admission_score))
    result: Result = await session.execute(query)
    student_list = result.all()

    students_to_add = []
    for index, (id_, score) in enumerate(student_list):
        status = "Одобрено" if index < 80 else "В очереди"

        query = select(Application).where(Application.student_id == index).limit(1)
        result: Result = await session.execute(query)
        student_list = result.scalars()

        if Application.preferred_dormitory is not None:
            wishes = True
        elif Application.preferred_floor is not None:
            wishes = True
        elif Application.first_preferred_student is not None:
            wishes = True
        else:
            wishes = False

        students_to_add.append(StudentListing(student_id=id_,
                                              admission_score=score,
                                              status=status,
                                              wishes=wishes))

    session.add_all(students_to_add)
    await session.commit()
    await status_update()
    await first_distribution()

    return [{"id": student[0], "admission_score": student[1]} for student in student_list]
