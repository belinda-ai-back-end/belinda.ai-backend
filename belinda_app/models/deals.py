from enum import Enum
from typing import TYPE_CHECKING, List
from decimal import Decimal
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .curators import Curator
    from .tracks import Track
    from .playlists import Playlist
    from .users import User


class TransactionStatusEnum(str, Enum):
    no_deal = "No deal"
    consideration = "Consideration"
    waiting = "Waiting"
    check = "Checking"
    complete = "Completed"


class Deal(SQLModel, table=True):
    deal_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    curator_id: UUID = Field(default=None, foreign_key="curator.curator_id")
    track_id: UUID = Field(default=None, foreign_key="track.track_id")
    playlist_id: str = Field(default=None, foreign_key="playlist.id")
    user_id: str = Field(default=None, foreign_key="user.user_id")
    price: Decimal | None
    status: TransactionStatusEnum | None = Field(default=TransactionStatusEnum.no_deal)
    curator: "Curator" = Relationship(back_populates="deal")
    track: "Track" = Relationship(back_populates="deal")
    playlist: "Playlist" = Relationship(back_populates="deal")
    user: "User" = Relationship(back_populates="deal")
