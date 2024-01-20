from typing import Annotated, cast

import strawberry
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from strawberry import ID

from flyps import db
from flyps.model import UserNoteTable
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
        q = q.where(UserNoteTable.user_id == user_id)
        notes = q.all()

        return UserNotes(
            notes=[
                UserNote(
                    id=cast(ID, note.id),
                    title=note.title,
                    content=note.content,
                )
                for note in notes
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

        return UserNote(
            id=cast(ID, note.id),
            title=note.title,
            content=note.content,
        )
