# from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


# if TYPE_CHECKING:
#     from .playlists import Playlist


class Track(SQLModel, table=True):
    track_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    id: str | None
    duration_ms: int | None
    name: str | None
    popularity: int | None
    preview_url: str | None
    album_id: str | None
    album_href: str | None
    album_name: str | None
    album_total_tracks: int | None
    artist_id: str | None
    artist_name: str | None
    artist_href: str | None
    playlist_id: str | None
    # playlist_id: str | None = Field(default=None, foreign_key="playlist.id")
    # playlist: Optional["Playlist"] = Relationship(back_populates="track")

