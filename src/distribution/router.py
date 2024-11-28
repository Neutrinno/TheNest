from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select, desc, and_, update, func, Result
from sqlalchemy.ext.asyncio import AsyncSession
from src.distribution.database import get_async_session
from src.distribution.schemas import StudentList
from src.models import Application, StudentListing, Room, Bed, Assignment, Dormitory, Status, User

router = APIRouter()

async def update_dormitory_occupancy(dormitory_id: int, session: AsyncSession):
    rooms_query = select(Room).where(and_(Room.dormitory_id == dormitory_id, Room.is_occupied == False))
    result: Result = await session.execute(rooms_query)
    remaining_rooms = result.scalars().all()

    if not remaining_rooms:
        statement = update(Dormitory).where(Dormitory.id == dormitory_id).values(is_occupied=True)
        await session.execute(statement)
        await session.commit()

    return {"message": "Статус общаги обновлен"}


async def find_free_room(dormitory_id: int, floor: int | None, session: AsyncSession):

    if floor:
        room_query = select(Room).where(and_(Room.dormitory_id == dormitory_id,
                                             Room.floor == floor,
                                             Room.is_occupied == False)).limit(1)
        result: Result = await session.execute(room_query)
        room_result = result.scalar_one_or_none()
    else:
        room_query = select(Room).where(and_(Room.dormitory_id == dormitory_id,
                                             Room.is_occupied == False)).limit(1)
        result: Result = await session.execute(room_query)
        room_result = result.scalar_one_or_none()

    return room_result


async def find_free_bed(room_id: int, session: AsyncSession):

    bed_query = select(Bed).where(and_(Bed.room_id == room_id, Bed.is_occupied == False)).limit(1)
    result: Result = await session.execute(bed_query)
    bed_result = result.scalar_one_or_none()

    return bed_result


async def assign_bed_to_student(student_id: int, bed_id: int, session: AsyncSession):

    assignment = Assignment(student_id=student_id,
                            bed_id=bed_id,
                            application_status="Место в общежитии предоставлено")
    session.add(assignment)

    statement = update(Bed).where(Bed.id == bed_id).values(is_occupied=True)
    await session.execute(statement)
    await session.commit()

    return {"message": "Запись в таблице \"assignment\"создана"}


async def handle_room_occupancy(room_id: int, session: AsyncSession):

    beds_query = select(Bed.id).where(and_(Bed.room_id == room_id, Bed.is_occupied == False))
    result: Result = await session.execute(beds_query)
    remaining_beds = len(result.scalars().all())

    if remaining_beds:
        statement = update(Room).where(Room.id == room_id).values(capacity=remaining_beds)
        await session.execute(statement)
    else:
        statement = update(Room).where(Room.id == room_id).values(is_occupied=True, capacity=0)
        await session.execute(statement)
    await session.commit()

    return {"message": "Заполнение комнаты обновлено"}


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


async def have_not_dormitory_wishes(application, all_dormitories, student, session: AsyncSession):
    try:
        for dormitory in all_dormitories:
            floor = application.preferred_floor
            room = await find_free_room(dormitory.id, floor, session)

            if room:
                bed = await find_free_bed(room.id, session)
                if bed:
                    await assign_bed_to_student(student.student_id, bed.id, session)
                    student.status = "Место в общежитии предоставлено"

                    await handle_room_occupancy(room.id, session)
                    await update_dormitory_occupancy(dormitory.id, session)

                    return {"status": "success","message": "Место успешно предоставлено"}
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


async def assign_roommates(session: AsyncSession):
    try:
        approved_students_query = select(StudentListing).where(
            and_(StudentListing.status == "Одобрено",
                 StudentListing.wishes == True))
        result = await session.execute(approved_students_query)
        approved_students = result.scalars().all()

        for student in approved_students:
            query = (select(Application).join(User, User.id == Application.student_id)
                .where(Application.student_id == student.student_id,
                    (Application.first_preferred_student.isnot(None) |
                     Application.second_preferred_student.isnot(None) |
                     Application.third_preferred_student.isnot(None))
                )
            )
            result = await session.execute(query)
            application = result.scalar_one_or_none()

            if application:

                preferred_emails = [application.first_preferred_student,
                                    application.second_preferred_student,
                                    application.third_preferred_student]
                preferred_emails = [email for email in preferred_emails if email]

                preferred_students_query = (select(User, Status).join(Status, Status.student_id == User.id)
                                            .where(User.email.in_(preferred_emails)))
                result: Result = await session.execute(preferred_students_query)
                preferred_students = result.scalars().all()

                assigned_students = [(user, status) for user, status in preferred_students
                                     if status.status == "Место в общежитии предоставлено"]
                unassigned_students = [(user, status) for user, status in preferred_students
                                       if status.status == "Одобрено"]

                if assigned_students:
                    for user, _ in assigned_students:
                        room_query = (select(Room).join(Bed, Bed.room_id == Room.id)
                                      .join(Assignment, Assignment.bed_id == Bed.id)
                                      .where(Assignment.student_id == user.id)
                                      .limit(1))
                        room_result: Result = await session.execute(room_query)
                        assigned_room = room_result.scalar_one_or_none()

                        if assigned_room:
                            # Проверить, есть ли свободная кровать в этой комнате
                            free_bed_query = (select(Bed).where(
                                and_(Bed.room_id == assigned_room.id, Bed.is_occupied == False)).limit(1))
                            free_bed_result: Result = await session.execute(free_bed_query)
                            free_bed = free_bed_result.scalar_one_or_none()

                            if free_bed:
                                # Подселяем нового студента на свободную кровать
                                await assign_bed_to_student(student.student_id, free_bed.id, session)
                                student.status = "Место в общежитии предоставлено"

                                await handle_room_occupancy(assigned_room.id, session)

                                dormitory_query = (select(Dormitory.id).join(Room, Room.dormitory_id == Dormitory.id)
                                      .where(Room.id == assigned_room.id).limit(1))
                                dormitory_result: Result = await session.execute(dormitory_query)
                                dormitory_id = dormitory_result.scalar_one_or_none()
                                await update_dormitory_occupancy(dormitory_id, session)

                                return {"status": "success", "message": "Студент успешно подселен",
                                        "data": {"room_id": assigned_room.id, "bed_id": free_bed.id}}
                        else:
                            continue

                else:
                    total_students = len(unassigned_students)
                    room_query = (select(Room).join(Bed, Bed.room_id == Room.id)
                        .where(Room.is_occupied == False,
                               Room.capacity >= total_students,
                               Bed.is_occupied == False)
                        .group_by(Room.id)
                        .having(func.count(Bed.id) >= total_students)
                        .limit(1))
                    room = (await session.execute(room_query)).scalar_one_or_none()

                    if room:
                        bed_query = (select(Bed)
                            .where(Bed.room_id == room.id, Bed.is_occupied == False)
                            .limit(total_students))
                        beds = (await session.execute(bed_query)).scalars().all()

                        for user, _ in unassigned_students:
                            bed = beds.pop()
                            await assign_bed_to_student(user.id, bed.id, session)
                            student.status = "Место в общежитии предоставлено"
                            await handle_room_occupancy(bed.room_id, session)

                        bed = beds.pop()
                        await assign_bed_to_student(application.student_id, bed.id, session)
                        student.status = "Место в общежитии предоставлено"
                        await handle_room_occupancy(bed.room_id, session)
                    else:
                        continue

        await session.commit()
        return {"status": "success", "message": "Распределение завершено успешно"}

    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": f"Произошла ошибка: {str(e)}"}


async def other_distribution(session: AsyncSession):
    try:

        approved_students_query = select(StudentListing).where(StudentListing.status == "Одобрено")
        result: Result = await session.execute(approved_students_query)
        approved_students = result.scalars().all()

        if not approved_students:
            return {"status": "success", "message": "Нет студентов для распределения"}

        dormitory_query = select(Dormitory)
        result: Result = await session.execute(dormitory_query)
        all_dormitories = result.scalars().all()

        if not all_dormitories:
            return {"status": "error", "message": "Нет доступных общежитий"}

        for student in approved_students:

            for dormitory in all_dormitories:
                room = await find_free_room(dormitory.id, floor=None, session=session)

                if room:
                    bed = await find_free_bed(room.id, session)

                    if bed:
                        await assign_bed_to_student(student.student_id, bed.id, session)
                        student.status = "Место в общежитии предоставлено"

                        await handle_room_occupancy(room.id, session)
                        await update_dormitory_occupancy(dormitory.id, session)
                        break


        await session.commit()

        return {"status": "success",
                "message": "Распределение завершено"}

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
        await assign_roommates(session)
        await other_distribution(session)
        await status_update(session)

        return [{"id": student[0], "admission_score": student[1]} for student in student_list]

    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": f"Произошла ошибка: {str(e)}"}