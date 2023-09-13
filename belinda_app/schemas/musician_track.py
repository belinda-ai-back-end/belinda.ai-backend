from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List


class CreateMusicianTrackRequest(BaseModel):
    trackName: Optional[str]
    genre: Optional[List[str]]
    trackLyricLanguage: Optional[str]
    songLyrics: Optional[str]
    track: Optional[str]
    trackLink: Optional[str]
    trackOverview: Optional[str]
    similarArtist: Optional[str]
    musician_id: Optional[UUID]
