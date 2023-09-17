from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from belinda_app.models import Curator, CuratorSession, CuratorPlaylist, CuratorSocialLink
from belinda_app.schemas import CreateCuratorRequest, CuratorEmail
from belinda_app.settings import get_settings
from belinda_app.db.database import SessionLocal

settings = get_settings()


class CuratorAuthorizationService:
    def __init__(self) -> None:
        self.session: AsyncSession = SessionLocal()

    async def register_curator(self, request: CreateCuratorRequest):

        existing_curator = await self.session.execute(select(Curator).where(Curator.email == request.email))
        existing_curator = existing_curator.first()
        if existing_curator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already registered.",
            )

        new_curator = Curator(
            email=request.email,
            password=request.password,
            name=request.name,
            desc=request.desc,
        )

        for pl in request.playlists:
            playlist = CuratorPlaylist(**pl.dict())
            new_curator.playlists.append(playlist)

        for sl in request.socialLinks:
            social_link = CuratorSocialLink(**sl.dict())
            new_curator.socialLinks.append(social_link)

        self.session.add(new_curator)

        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save curator information. : {e}",
            )

        return new_curator

    async def login_curator(self, request: CuratorEmail):
        curator = await self.session.execute(select(Curator).where(Curator.email == request.email))
        curator = curator.scalar()

        if curator is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        return curator

    async def logout_curator(self, curator_id: UUID):
        curator_session = await self.session.execute(
            select(CuratorSession).where(CuratorSession.curator_id == curator_id))
        curator_session = curator_session.scalar()

        if curator_session:
            curator_session.is_active = False
            await self.session.commit()

    async def create_curator_session(self, curator_id: UUID, access_token: str):
        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token_expires = datetime.utcnow() + expires_delta

        curator_session = await self.session.execute(
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
            self.session.add(curator_session)
        else:
            curator_session.access_token = access_token
            curator_session.access_token_expires = access_token_expires
            curator_session.is_active = True

        await self.session.commit()

        return curator_session
