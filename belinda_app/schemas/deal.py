from pydantic import BaseModel


class CreateDealRequest(BaseModel):
    curator_id: str
    track_id: str
    playlist_id: str
    user_id: str
    price: int

