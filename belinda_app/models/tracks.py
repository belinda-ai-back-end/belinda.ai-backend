from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Track(SQLModel, table=True):
    track_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    id: str | None
    durationMs: int | None
    name: str | None
    popularity: int | None
    previewUrl: str | None
    albumId: str | None
    albumHref: str | None
    albumName: str | None
    albumTotalTracks: int | None
    artistId: str | None
    artistName: str | None
    artistHref: str | None
    playlistId: str | None
