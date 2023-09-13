from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from belinda_app.db.database import SessionLocal
from belinda_app.models import Musician, MusicianTrack
from belinda_app.schemas import CreateMusicianTrackRequest


class MusicianTrackService:
    def __init__(self, track_data: CreateMusicianTrackRequest) -> None:
        self.session: AsyncSession = SessionLocal()
        self.track_data = track_data

    async def __call__(self) -> MusicianTrack:
        return await self.create_musician_track()

    async def create_musician_track(self) -> MusicianTrack:
        try:
            await self.get_musician_by_id(self.track_data.musician_id)
            new_track = MusicianTrack(**self.track_data.dict())
            self.session.add(new_track)
            await self.session.commit()
            await self.session.refresh(new_track)

            return new_track
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Track creation failed. Check your input data.")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_musician_by_id(self, musician_id: UUID):
        stmt = select(Musician).where(Musician.musician_id == musician_id)
        musician = await self.session.scalar(stmt)

        if not musician:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Musician with ID {musician_id} not found")
