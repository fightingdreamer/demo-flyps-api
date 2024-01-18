import strawberry

from flyps.redis import del_one, new_id, put_one
from flyps.user.types import User


@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def create(self, age: int, name: str) -> User:
        id = await new_id("user")
        user = User(id=id, age=age, name=name)
        await put_one("user", id, user)
        return user

    @strawberry.mutation
    async def delete(self, id: strawberry.ID) -> None:
        await del_one("user", id=id)
