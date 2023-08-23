from typing import List, TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .feedback import Feedback
    from .deals import Deal
    from .musician_track import MusicianTrack


class Musician(SQLModel, table=True):
    musician_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str | None
    email: str | None
    phone: str | None
    login: str | None
    password: str | None
    token: str | None
    artist_name: str | None
    artist_link: str | None
    origin: str | None
    musician_track_id: UUID = Field(default=None, foreign_key="musician_track.track_id")
    musician_track: Optional["MusicianTrack"] = Relationship(back_populates="musician")
    feedback: Optional[List["Feedback"]] = Relationship(back_populates="musician")
    deal: Optional[List["Deal"]] = Relationship(back_populates="musician")
