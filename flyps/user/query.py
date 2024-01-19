from typing import cast

import strawberry

from flyps import db
from flyps.model import UserTable
from flyps.user.types import User, Users


@strawberry.type
class UserQuery:
    @strawberry.field
    def get_all(self) -> Users:
        query = db.session.query(UserTable)
        users = query.all()
        return Users(
            users=[
                User(
                    id=cast(strawberry.ID, user.id),
                    age=user.age,
                    name=user.name,
                )
                for user in users
            ]
        )

    @strawberry.mutation
    def get_one(self, id: strawberry.ID) -> User:
        query = db.session.query(UserTable)
        query = query.where(UserTable.id == id)
        user = query.one()
        return User(
            id=cast(strawberry.ID, user.id),
            age=user.age,
            name=user.name,
        )
