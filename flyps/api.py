from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from flyps.graphql import schema

graphql_router = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_router, prefix="/graphql")
