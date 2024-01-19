from os import environ

import zstd
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

# ------------------------------------------------------------------------------

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# ------------------------------------------------------------------------------


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=naming_convention)


def create_session_factory():
    return sessionmaker(autoflush=False, autocommit=False)


def create_tables(base, engine):
    base.metadata.create_all(bind=engine)


# ------------------------------------------------------------------------------


def compress(value: bytes) -> bytes:
    if not value:
        return b""
    return zstd.compress(value, 1)


def decompress(value: bytes) -> bytes:
    if not value:
        return b""
    return zstd.decompress(value)


# ------------------------------------------------------------------------------


db_echo = environ.get("SQL_ECHO", False)
db_user = environ["POSTGRES_USER"]
db_pass = environ["POSTGRES_PASSWORD"]
db_name = environ["POSTGRES_DB"]

db_url = f"postgresql://{db_user}:{db_pass}@127.0.0.1/{db_name}"

# ------------------------------------------------------------------------------

Session = create_session_factory()
session = scoped_session(Session)

# ------------------------------------------------------------------------------


engine = create_engine(db_url, echo=db_echo)
Session.configure(bind=engine)
