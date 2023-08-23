from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel, Relationship


if TYPE_CHECKING:
    from .musician import Musician


class UserSession(SQLModel, table=True):
    __tablename__ = "".join(["_" + i.lower() if i.isupper() else i for i in __qualname__]).lstrip("_")  # noqa: F821

    session_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    musician_id: UUID = Field(default=None, foreign_key="musician.musician_id")
    access_token: str | None

    musician: Optional["Musician"] = Relationship(back_populates="user_session")

