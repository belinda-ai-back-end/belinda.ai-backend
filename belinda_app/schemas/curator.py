from typing import Optional, List, Tuple, Dict

from pydantic import BaseModel


class CreateCuratorRequest(BaseModel):
    email: Optional[str]
    password: Optional[str]
    name: Optional[str]
    desc: Optional[str]
    socialLinks: Optional[Dict[str, str]]
    playlists: Optional[List[Tuple[str, int]]]


class CuratorEmail(BaseModel):
    email: str
    password: str
