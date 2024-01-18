import strawberry

from flyps.user.mutation import UserMutation
from flyps.user.query import UserQuery


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> UserQuery:
        return UserQuery()


@strawberry.type
class Mutation:
    @strawberry.field
    def user(self) -> UserMutation:
        return UserMutation()


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
