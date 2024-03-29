import strawberry
from strawberry import ID

from flyps.user.note.types import UserNote

# ------------------------------------------------------------------------------


@strawberry.type
class User:
    id: strawberry.ID

    name: str
    notes: list[UserNote]


@strawberry.type
class Users:
    users: list[User]


# ------------------------------------------------------------------------------


@strawberry.type
class UserNotExistsError:
    id: ID
