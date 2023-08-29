from uuid import UUID, uuid4
from typing import List, TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .deals import Deal
    from .sessions import UserSession


class Curator(SQLModel, table=True):
    curator_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    login: str | None
    password: str | None
    name: str | None
    desc: str | None
    facebook_link: str | None
    spotify_link: str | None
    instagram_link: str | None
    tiktok_link: str | None
    twitter_link: str | None
    youtube_link: str | None
    apple_music_link: str | None
    mixcloud_link: str | None
    twitch_link: str | None

    deal: Optional[List["Deal"]] = Relationship(back_populates="curator")
    user_session: Optional[List["UserSession"]] = Relationship(back_populates="curator")
