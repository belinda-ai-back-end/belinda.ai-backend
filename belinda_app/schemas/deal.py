from pydantic import BaseModel
from belinda_app.models.deals import TransactionStatusEnum


class CreateDealRequest(BaseModel):
    curator_id: str
    track_id: str
    playlist_id: str
    user_id: str
    price: int


class UpdateDealStatusRequest(BaseModel):
    status: TransactionStatusEnum
