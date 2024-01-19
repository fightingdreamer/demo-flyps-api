import strawberry

from flyps.file.types import File
from flyps.redis import del_one, new_id, put_one


@strawberry.type
class FileMutation:
    @strawberry.mutation
    async def upload(self, name: str, data: str) -> File:
        id = await new_id("file")
        file = File(id=id, name=name, data=data)
        await put_one("file", id, file)
        return file

    @strawberry.mutation
    async def delete(self, id: strawberry.ID) -> None:
        await del_one("file", id=id)
