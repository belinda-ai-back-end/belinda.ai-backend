from enum import Enum
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship


if TYPE_CHECKING:
    from .musician import Musician
    from .curators import Curator


class UserRoleEnum(str, Enum):
    curator = "Curator"
    musician = "Musician"


class UserSession(SQLModel, table=True):
    __tablename__ = "".join(["_" + i.lower() if i.isupper() else i for i in __qualname__]).lstrip("_")  # noqa: F821

    session_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    musician_id: UUID = Field(default=None, foreign_key="musician.musician_id")
    curator_id: UUID = Field(default=None, foreign_key="curator.curator_id")
    user_role: UserRoleEnum | None
    access_token: str | None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(sa_column_kwargs={"default": datetime.utcnow})

    musician: Optional["Musician"] = Relationship(back_populates="user_session")
    curator: Optional["Curator"] = Relationship(back_populates="user_session")
