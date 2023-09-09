from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List

from belinda_app.models import GenreEnum


class CreateMusicianTrackRequest(BaseModel):
    track_name: Optional[str]
    genre: Optional[List[GenreEnum]]
    trackLyricLanguage: Optional[str]
    songLyrics: Optional[str]
    track: str  # File datatype
    trackLink: Optional[str]
    trackOverview: Optional[str]
    similarArtist: Optional[str]
    musician_id: Optional[UUID]
