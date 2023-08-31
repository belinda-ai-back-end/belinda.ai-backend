from typing import Optional

from pydantic import BaseModel


class CreateCuratorRequest(BaseModel):
    login: Optional[str]
    password: Optional[str]
    name: Optional[str]
    desc: Optional[str]
    facebook_link: Optional[str]
    spotify_link: Optional[str]
    instagram_link: Optional[str]
    tiktok_link: Optional[str]
    twitter_link: Optional[str]
    youtube_link: Optional[str]
    apple_music_link: Optional[str]
    mixcloud_link: Optional[str]
    twitch_link: Optional[str]


class CuratorLogin(BaseModel):
    login: str
    password: str
