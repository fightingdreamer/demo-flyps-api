import strawberry
from typing_extensions import cast

from flyps import db
from flyps.model import UserTable
from flyps.user.types import User


@strawberry.type
class UserMutation:
    @strawberry.mutation
    def create(self, age: int, name: str) -> User:
        user_row = UserTable(
            age=age,
            name=name,
        )
        db.session.add(user_row)
        db.session.commit()
        return User(
            id=cast(strawberry.ID, user_row.id),
            age=user_row.age,
            name=user_row.name,
        )

    @strawberry.mutation
    def delete(self, id: strawberry.ID) -> None:
        query = db.session.query(UserTable)
        query = query.where(UserTable.id == id)
        query.delete()
        db.session.commit()
