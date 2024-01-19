import strawberry


@strawberry.type
class File:
    id: strawberry.ID
    name: str
    data: str
