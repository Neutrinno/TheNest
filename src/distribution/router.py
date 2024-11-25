from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import Result, select, desc, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.distribution.database import get_async_session
from src.distribution.schemas import StudentList
from src.models import Application, StudentListing, Room, Bad, Assignment, Dormitory, Status

router = APIRouter()


async def floor_wishes(application, dormitory, student, session: AsyncSession):
    try:
        #Проверка на пожелания по этажу
        floor = application.preferred_floor
        #Поиск свободной комнаты на желанном этаже
        room_query = select(Room).where(and_(Room.dormitory_id == dormitory.id,
                                             Room.floor == floor,
                                             Room.is_occupied == False)).limit(1)
        room_result = await session.execute(room_query)
        room = room_result.scalar_one_or_none()
        #Проверка наличия свободной комнаты
        if not room:
            return {"status": "error", "message": "Нет свободных комнат на выбранном этаже"}
        #Поиск свободной кровати в комнате на желанном этаже
        bed_query = select(Bad).where(and_(Bad.room_id == room.id,
                                           Bad.is_occupied == False)).limit(1)
        bed_result = await session.execute(bed_query)
        bed = bed_result.scalar_one_or_none()
        #Проверка наличия свободной кровати
        if not bed:
            return {"status": "error", "message": "Нет свободных кроватей в комнате"}
        #Создание записи о присваивании комнаты
        assignment = Assignment(
            student_id=student.student_id,
            bad_id=bed.id,
            application_status="Место в общежитии предоставлено"
        )
        session.add(assignment)
        #Изменение статусов
        bed.is_occupied = True
        student.status = "Место в общежитии предоставлено"
        #Анализ коматы на свободную
        beds_query = select(Bad).where(and_(Bad.room_id == room.id,
                                            Bad.is_occupied == False))
        remaining_beds = await session.execute(beds_query)
        if not remaining_beds.scalar_one_or_none():
            room.is_occupied = True
        # Анализ общаги на свободную
        rooms_query = select(Room).where(and_(Room.dormitory_id == dormitory.id,
                                            Room.is_occupied == False))
        remaining_rooms = await session.execute(rooms_query)
        if not remaining_rooms.scalar_one_or_none():
            dormitory.is_occupied = True

        await session.commit()

        return {"status": "success","message": "Место успешно предоставлено",
                "data": {"room_id": room.id,"bed_id": bed.id, "floor": floor}}

    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": f"Произошла ошибка: {str(e)}"}


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


async def first_distribution(session: AsyncSession):
    #Поиск студентов с пожеланием и одобренными статусаи
    approved_students_query = select(StudentListing).join(Application).where(
        and_(
            StudentListing.status == "Одобрено",
            StudentListing.wishes == True
        )
    )
    result = await session.execute(approved_students_query)
    approved_students = result.scalars().all()
    #Перебор каждого студента из этого списка
    for student in approved_students:
        #Поиск заявки конкретного студента
        application_query = select(Application).where(Application.student_id == student.student_id).limit(1)
        result = await session.execute(application_query)
        application = result.scalar_one()
        #Запись и сопоставление студента и общаги
        dormitory_id = application.preferred_dormitory
        dormitory_query = select(Dormitory).where(Dormitory.id == dormitory_id).limit(1)
        dormitory_result = await session.execute(dormitory_query)
        dormitory = dormitory_result.scalar_one_or_none()

        if dormitory and dormitory.is_occupied == False:
            await floor_wishes(application, dormitory, student, session)

        elif dormitory is None:
            pass




"""
# Логика для подселения соседей
for neighbor_email in [application.first_preferred_student,
                       application.second_preferred_student,
                       application.third_preferred_student]:
    if neighbor_email:
        # Находим соседа по email
        neighbor_query = select(StudentListing).join(Application).where(
            and_(
                StudentListing.email == neighbor_email,
                StudentListing.status == "Одобрено"
            )
        ).limit(1)
        neighbor_result = await session.execute(neighbor_query)
        neighbor = neighbor_result.scalar_one_or_none()

        if neighbor:
            # Логика для подселения
            neighbor_application = await session.execute(
                select(Application).where(Application.student_id == neighbor.student_id).limit(1)
            )
            neighbor_application = neighbor_application.scalar_one()

            # Проверяем, если сосед тоже имеет статус "Одобрено", и подселяем их рядом
            if neighbor_application:
                # Здесь можно добавить дополнительную логику подселения соседей в те же комнаты
                pass

await session.commit()

# Распределение одобренных студентов без предпочтений
    pending_students_query = select(StudentListing).join(Application).where(and_(
            StudentListing.status == "Одобрено",
            StudentListing.wishes == True) )
    result = await session.execute(pending_students_query)
    pending_students = result.scalars().all()

    for student in pending_students:
        application_query = select(Application).where(Application.student_id == student.student_id).limit(1)
        result = await session.execute(application_query)
        application = result.scalar_one()

        # Проверка общежития и этажа
        dormitory_id = application.preferred_dormitory
        dormitory_query = select(Dormitory).where(Dormitory.id == dormitory_id).limit(1)
        dormitory_result = await session.execute(dormitory_query)
        dormitory = dormitory_result.scalar_one_or_none()

        if dormitory and dormitory.is_occupied == False:
            floor = application.preferred_floor
            room_query = select(Room).where(and_(
                Room.dormitory_id == dormitory_id,
                Room.floor == floor,
                Room.is_occupied == False
            )).limit(1)
            room_result = await session.execute(room_query)
            room = room_result.scalar_one_or_none()

            if room:
                # Проверка кровати
                bed_query = select(Bad).where(and_(
                    Bad.room_id == room.id,
                    Bad.is_occupied == False
                )).limit(1)
                bed_result = await session.execute(bed_query)
                bed = bed_result.scalar_one_or_none()

                if bed:
                    # Назначение кровати студенту
                    assignment = Assignment(
                        student_id=student.student_id,
                        bad_id=bed.id,
                        application_status="В ожидании"
                    )
                    session.add(assignment)

                    # Обновление состояния комнаты и кровати
                    room.is_occupied = True
                    bed.is_occupied = True

                    await session.commit()

    return {"message": "Распределение студентов завершено."}
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


"""async def floor_wishes(application, dormitory_id, student, session: AsyncSession):
    floor = application.preferred_floor
    room_query = select(Room).where(and_(Room.dormitory_id == dormitory_id,
                                         Room.floor == floor,
                                         Room.is_occupied == False)).limit(1)
    room_result = await session.execute(room_query)
    room = room_result.scalar_one_or_none()

    if room:
        bed_query = select(Bad).where(and_(Bad.room_id == room.id,
                                           Bad.is_occupied == False)).limit(1)
        bed_result = await session.execute(bed_query)
        bed = bed_result.scalar_one_or_none()

        if bed:

            assignment = Assignment(
                student_id=student.student_id,
                bad_id=bed.id,
                application_status="Место в общежитии предоставлено"
            )
            session.add(assignment)

            bed.is_occupied = True
            student.status = "Место в общежитии предоставлено"

        else:
            pass
    return"""