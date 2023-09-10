from typing import Optional, List

from pydantic import BaseModel


class SocialLink(BaseModel):
    name: str
    link: str


class Playlist(BaseModel):
    link: str
    cost: int


class CreateCuratorRequest(BaseModel):
    email: Optional[str]
    password: Optional[str]
    name: Optional[str]
    desc: Optional[str]
    socialLinks: Optional[List[SocialLink]]
    playlists: Optional[List[Playlist]]


class CuratorEmail(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True
