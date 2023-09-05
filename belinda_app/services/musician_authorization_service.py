from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from belinda_app.models import Musician, MusicianSession
from belinda_app.schemas import CreateMusicianRequest, MusicianLogin
from belinda_app.settings import get_settings


settings = get_settings()


class MusicianAuthorizationService:
    @classmethod
    async def register_musician(cls, session: AsyncSession, request: CreateMusicianRequest):
        existing_musician = await session.execute(select(Musician).where(Musician.login == request.login))
        existing_musician = existing_musician.scalar()

        if existing_musician:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This login is already registered.",
            )

        musician_data = request.dict()
        new_musician = Musician(**musician_data)

        session.add(new_musician)

        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save musician information.",
            )

        return new_musician

    @classmethod
    async def login_musician(cls, session: AsyncSession, request: MusicianLogin):
        musician = await session.execute(select(Musician).where(Musician.login == request.login))
        musician = musician.scalar()

        if musician is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return musician

    @classmethod
    async def logout_musician(cls, session: AsyncSession, musician_id: UUID):
        musician_session = await session.execute(
            select(MusicianSession).where(MusicianSession.musician_id == musician_id))
        musician_session = musician_session.scalar()

        if musician_session:
            musician_session.is_active = False
            await session.commit()

    @classmethod
    async def create_musician_session(cls, session: AsyncSession, musician_id: UUID, access_token: str):
        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token_expires = datetime.utcnow() + expires_delta

        musician_session = await session.execute(
            select(MusicianSession).where(MusicianSession.musician_id == musician_id)
        )
        musician_session = musician_session.scalar_one_or_none()

        if musician_session is None:
            musician_session = MusicianSession(
                musician_id=musician_id,
                access_token=access_token,
                access_token_expires=access_token_expires,
                is_active=True
            )
            session.add(musician_session)
        else:
            musician_session.access_token = access_token
            musician_session.access_token_expires = access_token_expires
            musician_session.is_active = True

        await session.commit()

        return musician_session
