from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select, desc, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.distribution.database import get_async_session
from src.distribution.schemas import StudentList
from src.models import Application, StudentListing, Room, Bed, Assignment, Dormitory, Status

router = APIRouter()


async def update_dormitory_occupancy(dormitory_id: int, session: AsyncSession):
    rooms_query = select(Room).where(and_(Room.dormitory_id == dormitory_id, Room.is_occupied == False))
    remaining_rooms = (await session.execute(rooms_query)).scalars().all()

    if not remaining_rooms:
        statement = update(Dormitory).where(Dormitory.id == dormitory_id).values(is_occupied=True)
        await session.execute(statement)
        await session.commit()


async def find_free_room(dormitory_id: int, floor: int, session: AsyncSession):

    room_query = select(Room).where(and_(Room.dormitory_id == dormitory_id,
                                         Room.floor == floor,
                                         Room.is_occupied == False)).limit(1)
    room_result = await session.execute(room_query)
    return room_result.scalar_one_or_none()


async def find_free_bed(room_id: int, session: AsyncSession):

    bed_query = select(Bed).where(and_(Bed.room_id == room_id, Bed.is_occupied == False)).limit(1)
    bed_result = await session.execute(bed_query)
    return bed_result.scalar_one_or_none()


async def assign_bed_to_student(student_id: int, bed_id: int, session: AsyncSession):

    assignment = Assignment(student_id=student_id,
                            bed_id=bed_id,
                            application_status="Место в общежитии предоставлено")
    session.add(assignment)

    statement = update(Bed).where(Bed.id == bed_id).values(is_occupied=True)
    await session.execute(statement)
    await session.commit()


async def handle_room_occupancy(room_id: int, session: AsyncSession):

    beds_query = select(Bed).where(and_(Bed.room_id == room_id, Bed.is_occupied == False))
    remaining_beds = await session.execute(beds_query)
    if not remaining_beds.scalars().first():
        statement = update(Room).where(Room.id == room_id).values(is_occupied=True)
        await session.execute(statement)
        await session.commit()


async def have_dormitory_wishes(application, dormitory, student, session: AsyncSession):
    try:
        floor = application.preferred_floor
        room = await find_free_room(dormitory.id, floor, session)

        if not room:
            return {"status": "error", "message": "Нет свободных комнат на выбранном этаже"}

        bed = await find_free_bed(room.id, session)
        if not bed:
            return {"status": "error", "message": "Нет свободных кроватей в комнате"}

        await assign_bed_to_student(student.student_id, bed.id, session)
        student.status = "Место в общежитии предоставлено"

        await handle_room_occupancy(room.id, session)
        await update_dormitory_occupancy(dormitory.id, session)

        return {"status": "success","message": "Место успешно предоставлено",
                "data": {"room_id": room.id, "bed_id": bed.id, "floor": floor}}

    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": f"Произошла ошибка: {str(e)}"}


async def have_not_dormitory_wishes(application, dormitories, student, session: AsyncSession):
    try:
        for dormitory in dormitories:
            floor = application.preferred_floor
            room = await find_free_room(dormitory.id, floor, session)

            if room:
                bed = await find_free_bed(room.id, session)
                if bed:
                    await assign_bed_to_student(student.student_id, bed.id, session)
                    student.status = "Место в общежитии предоставлено"

                    await handle_room_occupancy(room.id, session)
                    await update_dormitory_occupancy(dormitory.id, session)

                    return {"status": "success","message": "Место успешно предоставлено",
                            "data": {"dormitory_id": dormitory.id,
                                     "room_id": room.id,
                                     "bed_id": bed.id,
                                     "floor": floor}}
        return {"status": "error", "message": "Нет свободных мест во всех общежитиях"}

    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": f"Произошла ошибка: {str(e)}"}


async def status_update(session: AsyncSession):
    query = select(StudentListing).order_by(StudentListing.student_id)
    result = await session.execute(query)
    student_list = result.scalars().all()

    for student in student_list:
        new_status = student.status

        status_query = select(Status).where(Status.student_id == student.student_id).limit(1)
        status_result = await session.execute(status_query)
        status_record = status_result.scalar_one_or_none()

        if status_record:
            status_record.status = new_status

    await session.commit()
    return {"message": "Статусы успешно обновлены"}


async def first_distribution(session: AsyncSession):
    try:
        approved_students_query = select(StudentListing).where(
            and_(StudentListing.status == "Одобрено",
                 StudentListing.wishes == True))
        result = await session.execute(approved_students_query)
        approved_students = result.scalars().all()

        for student in approved_students:

            application_query = select(Application).where(Application.student_id == student.student_id).limit(1)
            result = await session.execute(application_query)
            application = result.scalar_one()

            dormitory_id = application.preferred_dormitory
            dormitory_query = select(Dormitory).where(Dormitory.id == dormitory_id).limit(1)
            dormitory_result = await session.execute(dormitory_query)
            dormitory = dormitory_result.scalar_one_or_none()

            if dormitory and not dormitory.is_occupied:
                await have_dormitory_wishes(application, dormitory, student, session)
            else:
                all_dormitories_query = select(Dormitory)
                all_dormitories_result = await session.execute(all_dormitories_query)
                all_dormitories = all_dormitories_result.scalars().all()

                await have_not_dormitory_wishes(application, all_dormitories, student, session)

        await session.commit()
        return {"status": "success", "message": "Распределение завершено успешно"}

    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": f"Произошла ошибка: {str(e)}"}



@router.get("/", response_model=list[StudentList])
async def get_distribution(session: AsyncSession = Depends(get_async_session)):
    try:
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
                wishes = any([application.preferred_dormitory is not None,
                              application.preferred_floor is not None,
                              application.first_preferred_student is not None,
                              application.second_preferred_student is not None,
                              application.third_preferred_student is not None])

                students_to_add.append(StudentListing(student_id=id_,
                                                      admission_score=score,
                                                      status=status,
                                                      wishes=wishes))
        session.add_all(students_to_add)
        await session.commit()

        await status_update(session)
        await first_distribution(session)

        return [{"id": student[0], "admission_score": student[1]} for student in student_list]

    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": f"Произошла ошибка: {str(e)}"}