import bcrypt
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from belinda_app.models import Curator, CuratorSession
from belinda_app.schemas import CreateCuratorRequest, CuratorLogin
from belinda_app.settings import get_settings


settings = get_settings()


class CuratorAuthorizationService:
    @classmethod
    async def register_curator(cls, session: AsyncSession, request: CreateCuratorRequest):
        existing_curator = await session.execute(select(Curator).where(Curator.login == request.login))
        existing_curator = existing_curator.scalar()

        if existing_curator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This login is already registered.",
            )

        hashed_password = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt())

        curator_data = request.dict(exclude={"password"})
        new_curator = Curator(**curator_data, password=hashed_password)

        session.add(new_curator)

        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save curator information.",
            )

        return new_curator

    @classmethod
    async def login_curator(cls, session: AsyncSession, request: CuratorLogin):
        curator = await session.execute(select(Curator).where(Curator.login == request.login))
        curator = curator.scalar()

        if curator is None or not bcrypt.checkpw(request.password.encode("utf-8"),
                                                 curator.password.encode("utf-8")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return curator

    @classmethod
    async def logout_curator(cls, session: AsyncSession, curator_id: UUID):
        curator_session = await session.execute(
            select(CuratorSession).where(CuratorSession.curator_id == curator_id))
        curator_session = curator_session.scalar()

        if curator_session:
            curator_session.is_active = False
            await session.commit()

    @classmethod
    async def create_curator_session(cls, session: AsyncSession, curator_id: UUID, access_token: str):
        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token_expires = datetime.utcnow() + expires_delta

        curator_session = await session.execute(
            select(CuratorSession).where(CuratorSession.curator_id == curator_id)
        )
        curator_session = curator_session.scalar_one_or_none()

        if curator_session is None:
            curator_session = CuratorSession(
                curator_id=curator_id,
                access_token=access_token,
                access_token_expires=access_token_expires,
                is_active=True
            )
            session.add(curator_session)
        else:
            curator_session.access_token = access_token
            curator_session.access_token_expires = access_token_expires
            curator_session.is_active = True

        await session.commit()

        return curator_session