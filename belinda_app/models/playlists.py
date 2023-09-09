from typing import List, TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .feedback import Feedback
    from .deals import Deal


class Playlist(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    collaborative: bool | None
    description: str | None
    externalUrlsSpotify: str | None
    href: str | None
    imagesUrl: str | None
    name: str | None
    ownerId: str | None
    ownerDisplayName: str | None
    ownerHref: str | None
    ownerShort: str | None
    primaryColor: str | None
    public: bool | None
    snapshotId: str | None
    tracksTotal: int
    type: str | None
    uri: str | None

    feedback: Optional[List["Feedback"]] = Relationship(back_populates="playlist")
    deal: Optional[List["Deal"]] = Relationship(back_populates="playlist")
