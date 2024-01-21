from typing import Annotated, cast

import strawberry
from sqlalchemy.exc import InternalError, NoResultFound
from strawberry import ID

from flyps import db, error
from flyps.model import UserNoteTable, UserTable
from flyps.user.note.types import UserNote, UserNoteNotExistsError, UserNotes
from flyps.user.types import UserNotExistsError

UserNoteGetallResponse = Annotated[
    UserNotes | UserNotExistsError,
    strawberry.union("UserNoteGetallResponse"),
]

UserNoteGetOneResponse = Annotated[
    UserNote | UserNoteNotExistsError,
    strawberry.union("UserNoteGetOneResponse"),
]


@strawberry.type
class UserNoteQuery:
    @strawberry.field
    async def get_all(self, user_id: ID) -> UserNoteGetallResponse:
        # warn: annotate schema in strawberry to make content optional
        q = db.session.query(UserTable)
        # warn: raise exception when user_id is not int
        q = q.where(UserTable.id == user_id)

        try:
            user = q.one()
        except NoResultFound:
            return UserNotExistsError(id=user_id)
        except InternalError:
            db.session.rollback()
            raise error.InternalError()

        return UserNotes(
            notes=[
                UserNote(
                    id=cast(ID, note.id),
                    title=note.title,
                    content=note.content,
                )
                for note in user.notes
            ]
        )

    @strawberry.mutation
    async def get_one(self, id: ID) -> UserNoteGetOneResponse:
        q = db.session.query(UserNoteTable)
        # warn: raise exception when id is not int
        q = q.where(UserNoteTable.id == id)

        try:
            note = q.one()
        except NoResultFound:
            return UserNoteNotExistsError(id=id)
        except InternalError:
            db.session.rollback()
            raise error.InternalError()

        return UserNote(
            id=cast(ID, note.id),
            title=note.title,
            content=note.content,
        )
