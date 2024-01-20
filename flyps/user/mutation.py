from typing import Annotated, cast

import strawberry
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy.sql import func
from strawberry import ID

from flyps import db
from flyps.error import InternalError
from flyps.model import UserTable
from flyps.user.types import User, UserNotExistsError


def get_alternative_user_name(name: str):
    q = db.session.query(UserTable.name)
    q = q.where(UserTable.name.startswith(name))
    q = q.order_by(func.char_length(UserTable.name))
    old_name = q.scalar()
    if not old_name:
        return name
    return old_name + "_"


@strawberry.type
class UserCreated:
    user: User


@strawberry.type
class UserNameAlreadyExistsError:
    alternative_name: str


UserCreateResponse = Annotated[
    UserCreated | UserNameAlreadyExistsError,
    strawberry.union("UserCreateResponse"),
]


@strawberry.type
class UserDeleted:
    id: ID


UserDeleteResponse = Annotated[
    UserDeleted | UserNotExistsError,
    strawberry.union("UserDeleteResponse"),
]


@strawberry.type
class UserMutation:
    @strawberry.mutation
    def create(self, name: str) -> UserCreateResponse:
        user = UserTable(
            name=name,
        )
        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            alternative_name = get_alternative_user_name(name)
            return UserNameAlreadyExistsError(
                alternative_name=alternative_name,
            )

        return UserCreated(
            user=User(
                id=cast(ID, user.id),
                name=user.name,
                notes=[],
            )
        )

    @strawberry.mutation
    def delete(self, id: ID) -> UserDeleteResponse:
        q = db.session.query(UserTable)
        q = q.where(UserTable.id == id)

        try:
            user = q.one()
        except NoResultFound:
            return UserNotExistsError(id=id)

        db.session.delete(user)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.exception(e)
            raise InternalError()

        return UserDeleted(id=id)
