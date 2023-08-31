from typing import Optional

from pydantic import BaseModel


class CreateMusicianRequest(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    login: Optional[str]
    password: Optional[str]
    artist_name: Optional[str]
    artist_link: Optional[str]
    origin: Optional[str]


class MusicianLogin(BaseModel):
    login: str
    password: str
