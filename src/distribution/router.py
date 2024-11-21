from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import Result, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.distribution.database import get_async_session
from src.distribution.schemas import StudentList
from src.models import Application, StudentListing, Status

router = APIRouter()

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


@router.get("/", response_model=list[StudentList])
async def get_distribution(session: AsyncSession = Depends(get_async_session)):
    query = select(Application.id, Application.admission_score).order_by(desc(Application.admission_score))
    result: Result = await session.execute(query)
    student_list = result.all()

    students_to_add = []
    for index, (id_, score) in enumerate(student_list):
        status = "Одобренно" if index < 67 else "В очереди"
        students_to_add.append(StudentListing(student_id=id_, admission_score=score, status=status))

    session.add_all(students_to_add)
    await session.commit()
    await status_update()

    return [{"id": student[0], "admission_score": student[1]} for student in student_list]
