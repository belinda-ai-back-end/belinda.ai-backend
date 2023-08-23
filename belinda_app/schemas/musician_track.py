from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class CreateMusicianTrackRequest(BaseModel):
    track_name: Optional[str]
    genre: Optional[str]
    track_lyric_language: Optional[str]
    song_lyric: Optional[str]
    track: str  # File datatype
    track_link: Optional[str]
    track_overview: Optional[str]
    similar_artist: Optional[str]
    musician_id: Optional[UUID]
