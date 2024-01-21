from typing import Annotated, cast

import strawberry
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import InternalError, NoResultFound
from strawberry import ID

from flyps.model import UserNoteTable
from flyps import db, error
from flyps.user.note.types import UserNote, UserNoteNotExistsError, UserNotes

UserNoteGetOneResponse = Annotated[
    UserNote | UserNoteNotExistsError,
    strawberry.union("UserNoteGetOneResponse"),
]


@strawberry.type
class UserNoteQuery:
    @strawberry.field
    async def get_all(self, user_id: ID) -> UserNotes:
        # warn: annotate schema in strawberry to make content optional
        q = db.session.query(UserNoteTable)
        q = q.options(joinedload(UserNoteTable.user))
        # warn: raise exception when user_id is not int
        q = q.where(UserNoteTable.user_id == user_id)

        try:
            user = q.one()
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
    async def get_one(self, id: ID) -> UserNote | UserNoteNotExistsError:
        q = db.session.query(UserNoteTable)
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
