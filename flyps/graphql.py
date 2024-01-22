import strawberry
from strawberry import Schema, field

from flyps.user.mutation import UserMutation
from flyps.user.note.query import (
    GetUserNoteResponse,
    GetUserNotesResponse,
    get_user_note,
    get_user_notes,
)
from flyps.user.query import GetUserResponse, GetUsersResponse, get_user, get_users


@strawberry.type
class Query:
    get_users: GetUsersResponse = field(resolver=get_users)
    get_user: GetUserResponse = field(resolver=get_user)
    get_user_notes: GetUserNotesResponse = field(resolver=get_user_notes)
    get_user_note: GetUserNoteResponse = field(resolver=get_user_note)


@strawberry.type
class Mutation:
    user: UserMutation = field(resolver=UserMutation)


schema = Schema(
    query=Query,
    mutation=Mutation,
)
