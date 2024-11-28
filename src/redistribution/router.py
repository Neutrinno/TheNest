from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.redistribution.database import get_async_session

router = APIRouter()

@router.get("/")
async def get_distribution(session: AsyncSession = Depends(get_async_session)):
    pass