from typing import List, TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .feedback import Feedback
    from .deals import Deal


class User(SQLModel, table=True):
    user_id: str = Field(default=None, primary_key=True)
    name: str | None
    email: str | None
    phone: str | None
    artist_name: str | None
    artist_link: str | None
    origin: str | None
    track_name: str | None
    genre: str | None
    track_lyric_language: str | None
    song_lyric: str | None
    track: str  # File datatype
    track_link: str | None
    track_overview: str | None
    similar_artist: str | None
    feedback: Optional[List["Feedback"]] = Relationship(back_populates="user")
    deal: Optional[List["Deal"]] = Relationship(back_populates="user")
