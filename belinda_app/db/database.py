from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

# from belinda_app.models import Feedback, User, Curator, Track, Playlist  # Добавление моделей в базу
from belinda_app.settings import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URI, pool_size=1000, max_overflow=64, pool_timeout=60, pool_pre_ping=True, echo=True)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def check_database_health() -> bool:
    try:
        async with SessionLocal() as session:
            await session.execute("SELECT 1")
            await session.commit()
            return True
    except SQLAlchemyError:
        return False
