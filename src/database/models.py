from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


id_pk = Annotated[str, mapped_column(String(36), primary_key=True)]
created_at_dt = Annotated[datetime, mapped_column(DateTime, default=func.now())]
updated_at_dt = Annotated[
    datetime, mapped_column(DateTime, default=func.now(), onupdate=func.now)
]


class FoldersOrm(Base):
    __tablename__ = "folders"

    id: Mapped[id_pk]
    path: Mapped[str] = mapped_column(String(255), unique=True)
    parent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[created_at_dt]
    updated_at: Mapped[updated_at_dt]


class FilesOrm(Base):
    __tablename__ = "files"

    __table_args__ = (UniqueConstraint("filename", "folder_id"),)

    id: Mapped[id_pk]
    filename: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[str | None] = mapped_column(String, nullable=True)
    size: Mapped[int] = mapped_column(BigInteger)
    folder_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("folders.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[created_at_dt]
    updated_at: Mapped[updated_at_dt]
    opened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
