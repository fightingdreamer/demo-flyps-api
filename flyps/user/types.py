import strawberry


@strawberry.type
class User:
    id: strawberry.ID
    age: int
    name: str

    # files: List[File]


@strawberry.type
class Users:
    users: list[User]
