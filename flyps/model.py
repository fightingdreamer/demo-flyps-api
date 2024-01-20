from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint

from flyps import db

# ------------------------------------------------------------------------------


class UserTable(db.Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(postgresql.INTEGER, primary_key=True)

    name: Mapped[str] = mapped_column(postgresql.TEXT, unique=True, nullable=False)

    notes: Mapped[list["UserNoteTable"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=True,
    )


# ------------------------------------------------------------------------------


class UserNoteTable(db.Base):
    __tablename__ = "user_note"
    __table_args__ = (UniqueConstraint("user_id", "title"),)
    id: Mapped[int] = mapped_column(postgresql.INTEGER, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False,
    )
    user: Mapped["UserTable"] = relationship(
        back_populates="notes",
        uselist=False,
    )

    title: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    content: Mapped[str] = mapped_column(postgresql.TEXT, nullable=True, default="")


db.create_tables(db.Base, db.engine)
