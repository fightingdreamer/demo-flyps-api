import strawberry
from strawberry import ID

# ------------------------------------------------------------------------------


@strawberry.type
class UserNote:
    id: ID

    title: str
    content: str


@strawberry.type
class UserNotes:
    notes: list[UserNote]


# ------------------------------------------------------------------------------


@strawberry.type
class UserNoteNotExistsError:
    id: ID
