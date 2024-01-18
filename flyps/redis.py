from pickle import dumps, loads
from typing import cast

import strawberry
from redis.asyncio.client import Redis

redis = Redis()


async def new_id(name: str) -> strawberry.ID:
    return cast(strawberry.ID, (await redis.incr("_" + name)))


async def get_all(name: str):
    value = await redis.hvals(name)
    return [loads(v) for v in value]


async def get_one(name: str, id: str):
    value = await redis.hget(name, id)
    if not value:
        raise ValueError()
    return loads(value)


async def put_one(name: str, id: str, payload: any):
    value = dumps(payload)
    await redis.hset(name, id, value)


async def del_one(name: str, id: str):
    await redis.hdel(name, id)
