from enum import Enum
from typing import TYPE_CHECKING, List

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .playlists import Playlist
    from .users import User


class RatingEnum(str, Enum):
    like = 'Like'
    dislike = 'Dislike'
    unlike = None


class Feedback(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    playlist_id: str | None = Field(default=None, foreign_key="playlist.id")
    user_id: str | None = Field(default=None, foreign_key="user.id")
    rating: RatingEnum | None = Field(default=RatingEnum.unlike)
    # like: bool | None = Field(default=None)
    # dislike: bool | None = Field(default=None)
    playlist: List["Playlist"] = Relationship(back_populates="feedback")
    user: "User" = Relationship(back_populates="feedback")
