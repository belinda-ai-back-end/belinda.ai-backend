from pydantic import BaseModel


class CreateMusicianRequest(BaseModel):
    name: str
    email: str | None
    phone: str | None
    login: str
    password: str
    artist_name: str | None
    artist_link: str | None
    origin: str | None
