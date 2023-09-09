from uuid import UUID, uuid4
from typing import List, TYPE_CHECKING, Optional, Tuple, Dict

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .deals import Deal
    from .curator_session import CuratorSession


class Curator(SQLModel, table=True):
    curator_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: str | None
    password: str | None
    name: str | None
    desc: str | None
    socialLinks: Dict[str, str] | None = Field(default=None, sa_column=Column(JSON))
    playlists: List[Tuple[str, int]] | None = Field(
        default=None,
        description="Playlists information (dictionary with link as key and (link, cost) as value).",
        sa_column=Column(JSON)
    )

    deal: Optional[List["Deal"]] = Relationship(back_populates="curator")
    user_session: Optional[List["CuratorSession"]] = Relationship(back_populates="curator")

    class Config:
        arbitrary_types_allowed = True
