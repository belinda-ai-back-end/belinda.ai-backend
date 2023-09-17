from typing import Union, Optional

from pydantic import BaseModel

from belinda_app.models import StatusKeyEnumForArtist, StatusKeyEnumForCurator


class CreateDealRequest(BaseModel):
    curator_id: Optional[str]
    playlist_id: Optional[str]
    artist_id: Optional[str]
    artist_track_id: Optional[str]
    price: Optional[int]
    status: Optional[Union[StatusKeyEnumForArtist, StatusKeyEnumForCurator]]
