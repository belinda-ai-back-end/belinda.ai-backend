from uuid import UUID, uuid4
from typing import List, TYPE_CHECKING, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .artist import Artist
    from .deals import Deal


class ArtistTrack(SQLModel, table=True):
    __tablename__ = "".join(["_" + i.lower() if i.isupper() else i for i in __qualname__]).lstrip("_")  # noqa: F821

    track_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    trackName: str | None
    genre: List[str] | None = Field(default=None, sa_column=Column(JSON))
    trackLyricLanguage: str | None
    songLyrics: str | None
    track: str | None
    trackLink: str | None
    trackOverview: str | None
    similarArtist: str | None
    artist_id: UUID = Field(default=None, foreign_key="artist.artist_id")

    artist: Optional[List["Artist"]] = Relationship(back_populates="artist_track")
    deal: Optional[List["Deal"]] = Relationship(back_populates="artist_track")

    class Config:
        arbitrary_types_allowed = True
