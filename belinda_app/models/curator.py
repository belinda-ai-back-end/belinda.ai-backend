from uuid import UUID, uuid4
from typing import List, TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .deals import Deal
    from .curator_session import CuratorSession
    from .curator_playlist import CuratorPlaylist
    from .curator_social_link import CuratorSocialLink


class Curator(SQLModel, table=True):
    curator_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: str | None
    password: str | None
    name: str | None
    desc: str | None

    socialLinks: List["CuratorSocialLink"] = Relationship(back_populates="curator")
    playlists: List["CuratorPlaylist"] = Relationship(back_populates="curator")

    deal: Optional[List["Deal"]] = Relationship(back_populates="curator")
    user_session: Optional[List["CuratorSession"]] = Relationship(back_populates="curator")
