from flyps.graphql import schema


async def user_create(*, age: int, name: str):
    return await schema.execute(
        """
        mutation UserCreate($age: Int!, $name: String!) {
            user {
                create(age: $age, name: $name) {
                    id
                    age
                    name
                }
            }
        }
        """,
        variable_values={
            "age": age,
            "name": name,
        },
    )


async def user_delete(*, id: int):
    return await schema.execute(
        """
        mutation UserDelete($id: ID!) {
            user {
                delete(id: $id)
            }
        }
        """,
        variable_values={
            "id": id,
        },
    )


def test_user(async_wait):
    result = async_wait(user_create(age=21, name="Vanessa"))
    assert result.errors is None

    result = async_wait(user_delete(id=result.data["user"]["create"]["id"]))
    assert result.errors is None
