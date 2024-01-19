import strawberry

from flyps.user.mutation import UserMutation
from flyps.user.query import UserQuery


@strawberry.type
class Query:
    user: UserQuery = strawberry.field(resolver=UserQuery)


@strawberry.type
class Mutation:
    user: UserMutation = strawberry.field(resolver=UserMutation)


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
