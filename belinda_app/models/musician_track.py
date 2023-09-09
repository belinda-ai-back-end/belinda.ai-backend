from enum import Enum
from uuid import UUID, uuid4
from typing import List, TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .musician import Musician
    from .deals import Deal


class GenreEnum(str, Enum):
    pop = "Pop"
    rock = "Rock"
    hip_hop = "Hip Hop"
    rap = "Rap"
    electronic = "Electronic"
    jazz = "Jazz"
    classical = "Classical"
    reggae = "Reggae"
    country = "Country"
    blues = "Blues"
    folk = "Folk"
    funk = "Funk"
    soul = "Soul"
    metal = "Metal"
    alternative = "Alternative"
    indie = "Indie"
    rnb = "R&B"
    dance = "Dance"
    punk = "Punk"
    techno = "Techno"
    house = "House"
    ambient = "Ambient"
    gospel = "Gospel"
    latin = "Latin"
    world = "World"
    soundtrack = "Soundtrack"
    other = "Other"


class MusicianTrack(SQLModel, table=True):
    __tablename__ = "".join(["_" + i.lower() if i.isupper() else i for i in __qualname__]).lstrip("_")  # noqa: F821

    track_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    track_name: str | None
    genre: List[GenreEnum] | None = Field(default=None)
    trackLyricLanguage: str | None
    songLyrics: str | None
    track: str  # File datatype
    trackLink: str | None
    trackOverview: str | None
    similarArtist: str | None
    musician_id: UUID = Field(default=None, foreign_key="musician.musician_id")

    musician: Optional[List["Musician"]] = Relationship(back_populates="musician_track")
    deal: Optional[List["Deal"]] = Relationship(back_populates="musician_track")
