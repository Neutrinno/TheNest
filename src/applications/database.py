from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import DB_USER, DB_PASS, DB_PORT, DB_NAME, DB_HOST

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo = True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

