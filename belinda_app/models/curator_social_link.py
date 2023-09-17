from uuid import UUID, uuid4
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship
from belinda_app.models import Curator


class CuratorSocialLink(SQLModel, table=True):
    __tablename__ = "".join(["_" + i.lower() if i.isupper() else i for i in __qualname__]).lstrip("_")  # noqa: F821

    curator_social_link_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str | None
    link: str | None

    curator_id: Optional[UUID] = Field(default=None, foreign_key="curator.curator_id")
    curator: Optional[Curator] = Relationship(back_populates="socialLinks")

