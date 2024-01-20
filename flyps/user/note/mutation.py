from typing import Annotated, cast

import strawberry
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy.sql import and_, func
from strawberry import ID

from flyps import db
from flyps.model import UserNoteTable
from flyps.user.note.types import UserNote, UserNoteNotExistsError


def get_alternative_note_title(user_id: ID, title: str):
    q = db.session.query(UserNoteTable.title)
    q = q.where(
        and_(UserNoteTable.user_id == user_id, UserNoteTable.title.startswith(title))
    )
    q = q.order_by(func.char_length(UserNoteTable.title))
    old_title = q.scalar()
    if not old_title:
        return title
    return old_title + "_"


@strawberry.type
class UserNoteCreated:
    note: UserNote


@strawberry.type
class UserNoteTitleAlreadyExistsError:
    alternative_title: str


UserNoteCreateResponse = Annotated[
    UserNoteCreated | UserNoteTitleAlreadyExistsError,
    strawberry.union("UserNoteCreateResponse"),
]


@strawberry.type
class UserNoteDeleted:
    id: ID


UserNoteDeleteResponse = Annotated[
    UserNoteDeleted | UserNoteNotExistsError,
    strawberry.union("UserNoteDeleteResponse"),
]


@strawberry.type
class UserNoteMutation:
    @strawberry.mutation
    def create(self, user_id: ID, title: str, content: str) -> UserNoteCreateResponse:
        note = UserNoteTable(
            user_id=user_id,
            title=title,
            content=content,
        )
        db.session.add(note)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            alternative_title = get_alternative_note_title(user_id, title)

            return UserNoteTitleAlreadyExistsError(
                alternative_title=alternative_title,
            )

        return UserNoteCreated(
            note=UserNote(
                id=cast(ID, note.id),
                title=note.title,
                content=note.content,
            )
        )

    @strawberry.mutation
    def delete(self, id: ID) -> UserNoteDeleteResponse:
        q = db.session.query(UserNoteTable)
        q = q.where(UserNoteTable.id == id)

        try:
            note = q.one()
        except NoResultFound:
            return UserNoteNotExistsError(id=id)

        db.session.delete(note)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            # warn: return global error from strawberry

        return UserNoteDeleted(id=id)
