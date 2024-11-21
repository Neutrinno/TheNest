from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import Result, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.distribution.database import get_async_session
from src.distribution.schemas import StudentList
from src.models import Application, StudentListing

router = APIRouter()


@router.get("/", response_model=list[StudentList])
async def get_distribution(session: AsyncSession = Depends(get_async_session)):
    query = select(Application.id, Application.admission_score).order_by(desc(Application.admission_score))
    result = await session.execute(query)
    student_list = result.all()

    students_to_add = [StudentListing(id=id_, admission_score=score) for id_, score in student_list]

    session.add_all(students_to_add)
    await session.commit()

    return [{"id": student[0], "admission_score": student[1]} for student in student_list]
