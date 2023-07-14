from enum import Enum
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .playlists import Playlist
    from .users import User


class RatingEnum(str, Enum):
    like = 'Like'
    dislike = 'Dislike'
    unlike = "No like/dislike"


class Feedback(SQLModel, table=True):
    feedback_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    playlist_id: str | None = Field(default=None, foreign_key="playlist.id")
    user_id: str | None = Field(default=None, foreign_key="user.id")
    rating: RatingEnum | None = Field(default=RatingEnum.unlike)
    playlist: List["Playlist"] = Relationship(back_populates="feedback")
    user: "User" = Relationship(back_populates="feedback")
