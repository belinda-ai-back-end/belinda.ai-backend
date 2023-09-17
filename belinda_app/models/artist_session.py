from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship


if TYPE_CHECKING:
    from .artist import Artist


class ArtistSession(SQLModel, table=True):
    __tablename__ = "".join(["_" + i.lower() if i.isupper() else i for i in __qualname__]).lstrip("_")  # noqa: F821

    session_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    artist_id: UUID = Field(default=None, foreign_key="artist.artist_id")
    access_token: str | None
    is_active: bool = Field(default=True)
    access_token_expires: datetime | None
    created_at: datetime = Field(sa_column_kwargs={"default": datetime.utcnow})

    artist: Optional["Artist"] = Relationship(back_populates="user_session")
