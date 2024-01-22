from typing import Annotated, cast

import strawberry
from sqlalchemy.exc import InternalError, NoResultFound
from strawberry import ID
from strawberry.types import Info

from flyps import db, error
from flyps.model import UserNoteTable, UserTable
from flyps.user.note.types import UserNote, UserNoteNotExistsError, UserNotes
from flyps.user.types import UserNotExistsError

GetUserNotesResponse = Annotated[
    UserNotes | UserNotExistsError,
    strawberry.union("UserNoteGetallResponse"),
]

GetUserNoteResponse = Annotated[
    UserNote | UserNoteNotExistsError,
    strawberry.union("UserNoteGetOneResponse"),
]


def get_user_notes(info: Info, user_id: ID) -> GetUserNotesResponse:
    # warn: annotate schema in strawberry to make content optional
    #       .options(load_only(*Table.column))
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


def get_user_note(info: Info, id: ID) -> GetUserNoteResponse:
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
