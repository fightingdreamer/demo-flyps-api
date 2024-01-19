import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from flyps.graphql import schema

graphql_router = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_router, prefix="/graphql")


def dev():
    uvicorn.run(
        "flyps.api:app",
        host="127.0.0.1",
        port=5000,
        log_level="info",
        reload=True,
        reload_delay=2,
        workers=1,
    )


def prd():
    uvicorn.run(
        "flyps.api:app",
        host="0.0.0.0",
        port=5000,
        log_level="info",
        reload=False,
        workers=4,
    )
