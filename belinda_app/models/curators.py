from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Curator(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
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
