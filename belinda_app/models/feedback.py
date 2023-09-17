from enum import Enum
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .playlists import Playlist
    from .artist import Artist


class RatingEnum(str, Enum):
    like = "Like"
    dislike = "Dislike"
    unlike = "No like/dislike"


class Feedback(SQLModel, table=True):
    feedback_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    playlist_id: str = Field(default=None, foreign_key="playlist.id")
    artist_id: UUID = Field(default=None, foreign_key="artist.artist_id")
    rating: RatingEnum | None = Field(default=RatingEnum.unlike)

    playlist: List["Playlist"] = Relationship(back_populates="feedback")
    artist: "Artist" = Relationship(back_populates="feedback")
