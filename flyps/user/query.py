from typing import Annotated, cast

import strawberry
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from strawberry import ID

from flyps import db
from flyps.model import UserTable
from flyps.user.note.types import UserNote
from flyps.user.types import User, UserNotExistsError, Users

UserGetOneResponse = Annotated[
    User | UserNotExistsError,
    strawberry.union("UserGetOneResponse"),
]


@strawberry.type
class UserQuery:
    @strawberry.field
    def get_all(self) -> Users:
        q = db.session.query(UserTable)
        # warn: annotate schema in strawberry to make notes excluded
        q = q.options(joinedload(UserTable.notes))
        users = q.all()
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

    @strawberry.mutation
    def get_one(self, id: ID) -> UserGetOneResponse:
        q = db.session.query(UserTable)
        # warn: annotate schema in strawberry to make notes optional
        q = q.options(joinedload(UserTable.notes))
        q = q.where(UserTable.id == id)

        try:
            user = q.one()
        except NoResultFound:
            return UserNotExistsError(id=id)

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
