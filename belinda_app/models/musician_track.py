from uuid import UUID, uuid4
from typing import List, TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .musician import Musician
    from .deals import Deal


class MusicianTrack(SQLModel, table=True):
    __tablename__ = "".join(["_" + i.lower() if i.isupper() else i for i in __qualname__]).lstrip("_")  # noqa: F821

    track_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    track_name: str | None
    genre: str | None
    track_lyric_language: str | None
    song_lyric: str | None
    track: str  # File datatype
    track_link: str | None
    track_overview: str | None
    similar_artist: str | None
    musician_id: UUID = Field(default=None, foreign_key="musician.musician_id")

    musician: Optional[List["Musician"]] = Relationship(back_populates="musician_track")
    deal: Optional[List["Deal"]] = Relationship(back_populates="musician_track")
