import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.models import Base, StudentListing, Assignment, Status
from src.applications.database import get_async_session
from src.redistribution.router import router as redistribution_router
from src.applications.router import router as application_router

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session_test() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


app = FastAPI()
app.include_router(redistribution_router)
app.include_router(application_router)

app.dependency_overrides[get_async_session] = get_async_session_test


@pytest.mark.asyncio
async def test_get_confirmation():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        students = [StudentListing(student_id=1, admission_score=90, status="Принято", wishes=True),
                    StudentListing(student_id=2, admission_score=80, status="Принято", wishes=True)]

        assignments = [Assignment(id=1, student_id=1, bed_id=1, application_status="Принято"),
                       Assignment(id=2, student_id=2, bed_id=2, application_status="Принято")]

        statuses = [Status(application_id=1, student_id=1, status="Принято"),
                    Status(application_id=2, student_id=2, status="Принято")]

        session.add_all(students + assignments + statuses)
        await session.commit()


    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        response = await client.put(f"/get_confirmation/{1}")
        assert response.status_code == 200
        assert response.json() == "Подтверждение получено"

    async with async_session_maker() as session:
        result = await session.execute(select(StudentListing).order_by(StudentListing.student_id))
        updated_students = result.scalars().all()

        assert updated_students[0].status == "Подтвержден"
        assert updated_students[1].status == "Принято"

        assignment = await session.execute(select(Assignment).where(Assignment.student_id == 1))
        updated_assignment = assignment.scalar()
        assert updated_assignment.application_status == "Подтвержден"

        status = await session.execute(select(Status).where(Status.student_id == 1))
        updated_status = status.scalar()
        assert updated_status.status == "Подтвержден"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

