import strawberry

from flyps.user.mutation import UserMutation
from flyps.user.note.mutation import UserNoteMutation
from flyps.user.note.query import UserNoteQuery
from flyps.user.query import UserQuery


@strawberry.type
class Query:
    user: UserQuery = strawberry.field(resolver=UserQuery)
    user_note: UserNoteQuery = strawberry.field(resolver=UserNoteQuery)


@strawberry.type
class Mutation:
    user: UserMutation = strawberry.field(resolver=UserMutation)
    user_note: UserNoteMutation = strawberry.field(resolver=UserNoteMutation)


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
