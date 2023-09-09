from typing import Optional

from pydantic import BaseModel


class CreateMusicianRequest(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    password: Optional[str]
    ArtistName: Optional[str]
    # ArtistLink: Optional[str]
    origin: Optional[str]


class MusicianEmail(BaseModel):
    email: str
    password: str
