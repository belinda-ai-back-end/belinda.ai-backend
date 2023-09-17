from typing import List, TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .feedback import Feedback
    from .deals import Deal
    from .artist_track import ArtistTrack
    from .artist_session import ArtistSession


class Artist(SQLModel, table=True):
    artist_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str | None
    phone: str | None
    email: str | None
    password: str | None
    artistName: str | None
    # artistLink: str | None
    origin: str | None

    artist_track: Optional["ArtistTrack"] = Relationship(back_populates="artist")
    feedback: Optional[List["Feedback"]] = Relationship(back_populates="artist")
    deal: Optional[List["Deal"]] = Relationship(back_populates="artist")
    user_session: Optional[List["ArtistSession"]] = Relationship(back_populates="artist")
