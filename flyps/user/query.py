from typing import Annotated, cast

import strawberry
from sqlalchemy.exc import InternalError, NoResultFound
from sqlalchemy.orm import joinedload
from strawberry import ID
from strawberry.types import Info

from flyps import db, error
from flyps.model import UserTable
from flyps.user.note.types import UserNote
from flyps.user.types import User, UserNotExistsError, Users

GetUsersResponse = Annotated[
    Users,
    strawberry.union("GetUsersResponse"),
]

GetUserResponse = Annotated[
    User | UserNotExistsError,
    strawberry.union("GetUserResponse"),
]


def get_users(info: Info) -> GetUsersResponse:
    q = db.session.query(UserTable)
    # warn: annotate schema in strawberry to make notes excluded
    q = q.options(joinedload(UserTable.notes))

    try:
        users = q.all()
    except InternalError:
        db.session.rollback()
        raise error.InternalError()

    return Users(
        users=[
            User(
                id=cast(ID, user.id),
                name=user.name,
                notes=[
                    UserNote(
                        id=cast(ID, note.id),
                        title=note.title,
                        content=note.content,
                    )
                    for note in user.notes
                ],
            )
            for user in users
        ]
    )


def get_user(info: Info, id: ID) -> GetUserResponse:
    q = db.session.query(UserTable)
    # warn: annotate schema in strawberry to make notes optional
    q = q.options(joinedload(UserTable.notes))
    # warn: raise exception when id is not int
    q = q.where(UserTable.id == id)

    try:
        user = q.one()
    except NoResultFound:
        return UserNotExistsError(id=id)
    except InternalError:
        db.session.rollback()
        raise error.InternalError()

    return User(
        id=cast(ID, user.id),
        name=user.name,
        notes=[
            UserNote(
                id=cast(ID, note.id),
                title=note.title,
                content=note.content,
            )
            for note in user.notes
        ],
    )
