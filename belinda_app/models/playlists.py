from typing import List, TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .feedback import Feedback
    from .deals import Deal


class Playlist(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    collaborative: bool | None
    description: str | None
    external_urls_spotify: str | None
    href: str | None
    images_url: str | None
    name: str | None
    owner_id: str | None
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
    deal: Optional[List["Deal"]] = Relationship(back_populates="playlist")
