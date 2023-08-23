from pydantic import BaseModel


class CreateDealRequest(BaseModel):
    curator_id: str
    playlist_id: str
    musician_id: str
    musician_track_id: str
    price: int

