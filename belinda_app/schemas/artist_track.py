from pydantic import BaseModel
from typing import Optional, List


class CreateArtistTrackRequest(BaseModel):
    trackName: Optional[str]
    genre: Optional[List[str]]
    trackLyricLanguage: Optional[str]
    songLyrics: Optional[str]
    track: Optional[str]
    trackLink: Optional[str]
    trackOverview: Optional[str]
    similarArtist: Optional[str]
