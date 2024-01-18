import strawberry

from flyps.redis import get_all, get_one
from flyps.user.types import User, Users


@strawberry.type
class UserQuery:
    @strawberry.field
    async def get_all(self) -> Users:
        return Users(users=await get_all("user"))

    @strawberry.mutation
    async def get_one(self, id: strawberry.ID) -> User:
        return await get_one("user", id)
