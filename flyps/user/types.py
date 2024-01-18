import strawberry


@strawberry.type
class User:
    id: strawberry.ID
    age: int
    name: str


@strawberry.type
class Users:
    users: list[User]
