from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from belinda_app.models import Artist, ArtistSession
from belinda_app.schemas import CreateArtistRequest, ArtistEmail
from belinda_app.settings import get_settings
from belinda_app.db.database import SessionLocal

settings = get_settings()


class ArtistAuthorizationService:
    def __init__(self) -> None:
        self.session: AsyncSession = SessionLocal()

    async def register_artist(self, request: CreateArtistRequest):
        existing_artist = await self.session.execute(select(Artist).where(Artist.email == request.email))
        existing_artist = existing_artist.scalar()

        if existing_artist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already registered.",
            )

        artist_data = request.dict()
        new_artist = Artist(**artist_data)

        self.session.add(new_artist)

        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save artist information.",
            )

        return new_artist

    async def login_artist(self, request: ArtistEmail):
        artist = await self.session.execute(select(Artist).where(Artist.email == request.email))
        artist = artist.scalar()

        if artist is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        return artist

    async def logout_artist(self, artist_id: UUID):
        artist_session = await self.session.execute(
            select(ArtistSession).where(ArtistSession.artist_id == artist_id))
        artist_session = artist_session.scalar()

        if artist_session:
            artist_session.is_active = False
            await self.session.commit()

    async def create_artist_session(self, artist_id: UUID, access_token: str):
        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token_expires = datetime.utcnow() + expires_delta

        artist_session = await self.session.execute(
            select(ArtistSession).where(ArtistSession.artist_id == artist_id)
        )
        artist_session = artist_session.scalar_one_or_none()

        if artist_session is None:
            artist_session = ArtistSession(
                artist_id=artist_id,
                access_token=access_token,
                access_token_expires=access_token_expires,
                is_active=True
            )
            self.session.add(artist_session)
        else:
            artist_session.access_token = access_token
            artist_session.access_token_expires = access_token_expires
            artist_session.is_active = True

        await self.session.commit()

        return artist_session
