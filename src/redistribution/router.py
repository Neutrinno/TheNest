from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import StudentListing, Assignment, Status
from src.redistribution.database import get_async_session

router = APIRouter()

@router.get("/", response_model=str)
async def get_redistribution(session: AsyncSession = Depends(get_async_session)):
    query = select(StudentListing).order_by(StudentListing.admission_score)
    result = await session.execute(query)
    student_list = result.scalars().all()

    accepted = [student for student in student_list if student.status == "Принято"]
    waiting = [student for student in student_list if student.status == "Ожидает очереди"]

    for student in accepted:
        student_listing_stmt = update(StudentListing).where(StudentListing.student_id == student.student_id).values(status="Отклонено")
        await session.execute(student_listing_stmt)

        status_stmt = update(Status).where(Status.student_id == student.student_id).values(status="Отклонено")
        await session.execute(status_stmt)

        if waiting:
            new_student = waiting.pop(0)
            assignment_stmt = update(Assignment).where(Assignment.student_id == student.student_id).values(student_id=new_student.student_id)
            await session.execute(assignment_stmt)

            new_student_stmt = update(StudentListing).where(StudentListing.student_id == new_student.student_id).values(status="Принято")
            await session.execute(new_student_stmt)

            new_status_stmt = update(Status).where(Status.student_id == new_student.student_id).values(status="Принято")
            await session.execute(new_status_stmt)
        else:
            await session.commit()
            return "Студенты закончились"

    await session.commit()
    return "Перераспределение прошло успешно"