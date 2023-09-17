from typing import Optional

from pydantic import BaseModel


class CreateArtistRequest(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    password: Optional[str]
    artistName: Optional[str]
    # artistLink: Optional[str]
    origin: Optional[str]


class ArtistEmail(BaseModel):
    email: str
    password: str
