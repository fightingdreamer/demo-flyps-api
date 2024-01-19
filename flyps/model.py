from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from flyps import db

# ------------------------------------------------------------------------------


class UserTable(db.Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(postgresql.INTEGER, primary_key=True)

    age: Mapped[int] = mapped_column(postgresql.SMALLINT, nullable=False)
    name: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)

    files: Mapped[list["FileTable"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=True,
    )


# ------------------------------------------------------------------------------


class FileTable(db.Base):
    __tablename__ = "file"
    id: Mapped[int] = mapped_column(postgresql.INTEGER, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False,
    )
    user: Mapped["UserTable"] = relationship(
        back_populates="files",
        uselist=False,
    )

    name: Mapped[str] = mapped_column(postgresql.TEXT, nullable=True)
    data_zstd: Mapped[bytes] = mapped_column(
        postgresql.BYTEA, nullable=False, default=b""
    )

    @property
    def data(self):
        return db.decompress(self.data_zstd).decode()

    @data.setter
    def data(self, value):
        self.data_zstd = db.compress(value.encode())


db.create_tables(db.Base, db.engine)
