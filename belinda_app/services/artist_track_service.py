from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from belinda_app.db.database import SessionLocal
from belinda_app.models import ArtistTrack
from belinda_app.schemas import CreateArtistTrackRequest


class ArtistTrackService:
    def __init__(self, track_data: CreateArtistTrackRequest, artist_id: UUID) -> None:
        self.session: AsyncSession = SessionLocal()
        self.artist_id = artist_id
        self.track_data = track_data

    async def __call__(self) -> ArtistTrack:
        return await self.create_artist_track()

    async def create_artist_track(self) -> ArtistTrack:
        try:
            # await self.get_artist_by_id(self.track_data.artist_id)
            new_track = ArtistTrack(artist_id=self.artist_id, **self.track_data.dict())
            self.session.add(new_track)
            await self.session.commit()
            await self.session.refresh(new_track)

            return new_track
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Track creation failed. Check your input data.")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
