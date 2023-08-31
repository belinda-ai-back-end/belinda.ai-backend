from datetime import datetime

from pydantic import BaseModel
from uuid import UUID


class MusicianSessionSchema(BaseModel):
    session_id: UUID
    musician_id: UUID
    access_token: str
    access_token_expires: datetime
    is_active: bool
    created_at: datetime
