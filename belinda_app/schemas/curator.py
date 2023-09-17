from typing import Optional, List

from pydantic import BaseModel


class SocialLinkSchemas(BaseModel):
    name: Optional[str]
    link: Optional[str]


class CuratorPlaylistSchemas(BaseModel):
    link: Optional[str]
    cost: Optional[int]


class CreateCuratorRequest(BaseModel):
    email: Optional[str]
    password: Optional[str]
    name: Optional[str]
    desc: Optional[str]
    socialLinks: Optional[List[SocialLinkSchemas]]
    playlists: Optional[List[CuratorPlaylistSchemas]]


class CuratorEmail(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True
