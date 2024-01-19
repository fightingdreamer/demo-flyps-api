import strawberry

from flyps.photo.types import Photo, Photos
from flyps.redis import get_all, get_one


@strawberry.type
class PhotoQuery:
    @strawberry.field
    async def get_all(self) -> Photos:
        return Photos(photos=await get_all("photo"))

    @strawberry.mutation
    async def get_one(self, id: strawberry.ID) -> Photo:
        return await get_one("photo", id)
