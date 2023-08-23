from enum import Enum
from typing import TYPE_CHECKING, Optional
from decimal import Decimal
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .curators import Curator
    from .playlists import Playlist
    from .musician import Musician
    from .musician_track import MusicianTrack


class StatusKeyEnumForMusician(str, Enum):
    submit = "Submit Application"
    awaiting = "Awaiting review"
    confirmed_payment = "Confirmed, awaiting payment"
    confirmed_placement = "Confirmed, awaiting placement"
    payment = "Placed - x days left until completion"
    completed = "Completed, can be extended"


class StatusKeyEnumForCurator(str, Enum):
    confirm = "Confirm / Reject"
    confirmed_payment_curator = "Confirmed, awaiting payment"
    confirmed_placement_curator = "Confirmed, awaiting placement"
    payment_curator = "Placed - x days left until completion"
    completed_curator = "Completed, can be extended"


class Deal(SQLModel, table=True):
    deal_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    curator_id: UUID = Field(default=None, foreign_key="curator.curator_id")
    playlist_id: str = Field(default=None, foreign_key="playlist.id")
    musician_track_id: UUID = Field(default=None, foreign_key="musician_track.track_id")
    musician_id: UUID = Field(default=None, foreign_key="musician.musician_id")
    price: Decimal | None
    status: StatusKeyEnumForMusician | None = Field(default=StatusKeyEnumForMusician.submit)

    curator: Optional["Curator"] = Relationship(back_populates="deal")
    playlist: Optional["Playlist"] = Relationship(back_populates="deal")
    musician_track: Optional["MusicianTrack"] = Relationship(back_populates="deal")
    musician: Optional["Musician"] = Relationship(back_populates="deal")
