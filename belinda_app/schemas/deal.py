from typing import Union, Optional

from pydantic import BaseModel

from belinda_app.models import StatusKeyEnumForMusician, StatusKeyEnumForCurator


class CreateDealRequest(BaseModel):
    curator_id: Optional[str]
    playlist_id: Optional[str]
    musician_id: Optional[str]
    musician_track_id: Optional[str]
    price: Optional[int]
    status: Optional[Union[StatusKeyEnumForMusician, StatusKeyEnumForCurator]]
