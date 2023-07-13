from typing import List, TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .curators import Curator
    from .feedback import Feedback


class Playlist(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    collaborative: bool | None
    description: str | None
    external_urls_spotify: str | None
    href: str | None
    images_url: str | None
    name: str | None
    owner_id: UUID | None = Field(default_factory=uuid4, foreign_key="curator.id")
    owner_display_name: str | None
    owner_href: str | None
    owner_short: str | None
    primary_color: str | None
    public: bool | None
    snapshot_id: str | None
    tracks_total: int
    type: str | None
    uri: str | None
    feedback: Optional[List["Feedback"]] = Relationship(back_populates="playlist")
    owner: Optional["Curator"] = Relationship(back_populates="playlist")
