import pytest

from flyps import db
from flyps.graphql import schema
from flyps.model import UserNoteTable, UserTable
from flyps.util.operator import itempathgetter

# ------------------------------------------------------------------------------


async def user_create(*, name: str):
    return await schema.execute(
        """
        mutation Create($name: String!) {
            user {
                create(name: $name) {
                    __typename
                    ... on UserNameAlreadyExistsError {
                            alternativeName
                        }
                    ... on UserCreated {
                        user {
                            id
                            name
                        }
                    }
                }
            }
        }
        """,
        variable_values={
            "name": name,
        },
    )


async def user_getall():
    return await schema.execute(
        """
        query GetAll {
            user {
                getAll {
                    users {
                        id
                        name
                    }
                }
            }
        }
        """,
        variable_values={},
    )


async def user_getone(*, id: int):
    return await schema.execute(
        """
        query GetOne($id: ID!) {
            user {
                getOne(id: $id) {
                    __typename
                    ... on UserNotExistsError {
                            id
                        }
                    ... on User {
                            id
                            name
                            notes {
                                id
                                title
                            }
                        }
                }
            }
        }
        """,
        variable_values={"id": id},
    )


async def user_delete(*, id: int):
    return await schema.execute(
        """
        mutation Delete($id: ID!) {
            user {
                delete(id: $id) {
                    __typename
                    ... on UserNotExistsError {
                            id
                        }
                    ... on UserDeleted {
                            id
                        }
                }
            }
        }
        """,
        variable_values={
            "id": id,
        },
    )


# ------------------------------------------------------------------------------


async def user_note_create(*, user_id: int, title: str, content: str):
    return await schema.execute(
        """
        mutation Create($userId: ID!, $title: String!, $content: String!) {
            userNote {
                create(userId: $userId, title: $title, content: $content) {
                    __typename
                    ... on UserNoteTitleAlreadyExistsError {
                            alternativeTitle
                        }
                    ... on UserNoteCreated {
                        note {
                            id
                            title
                            content
                        }
                    }
                }
            }
        }
        """,
        variable_values={
            "title": title,
            "userId": user_id,
            "content": content,
        },
    )


async def user_note_getall(*, user_id: int):
    return await schema.execute(
        """
        query GetAll($userId: ID!) {
            userNote {
                getAll(userId: $userId) {
                    notes {
                        id
                        title
                        content
                    }
                }
            }
        }
        """,
        variable_values={
            "userId": user_id,
        },
    )


async def user_note_getone(*, id: int):
    return await schema.execute(
        """
        query GetOne($id: ID!) {
            userNote {
                getOne(id: $id) {
                    __typename
                    ... on UserNoteNotExistsError {
                            id
                        }
                    ... on UserNote {
                            id
                            title
                            content
                        }
                }
            }
        }
        """,
        variable_values={"id": id},
    )


async def user_note_delete(*, id: int):
    return await schema.execute(
        """
        mutation Delete($id: ID!) {
            userNote {
                delete(id: $id) {
                    __typename
                    ... on UserNoteNotExistsError {
                            id
                        }
                    ... on UserNoteDeleted {
                            id
                        }
                }
            }
        }
        """,
        variable_values={
            "id": id,
        },
    )


# ------------------------------------------------------------------------------


def _v(value, path):
    return itempathgetter(path)(value)


def _db_user_id(name: str):
    return db.session.query(UserTable.id).where(UserTable.name == name).scalar()


def _db_note_id(title: str):
    return (
        db.session.query(UserNoteTable.id).where(UserNoteTable.title == title).scalar()
    )


skip_db_not_test = pytest.mark.skipif(
    not db.db_name.endswith("-test"),
    reason=f"'{db.db_name}' is not a test database",
)


@skip_db_not_test
def test_delete_database():
    db.delete_database(db.engine, db.db_url)


@skip_db_not_test
def test_ensure_database():
    db.ensure_database(db.engine, db.db_url)


@skip_db_not_test
def test_create_tables():
    db.create_tables(db.Base, db.engine)


@skip_db_not_test
def test_user_create(async_wait):
    user_id = _db_user_id("TestUser")
    if user_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_create(name="TestUser")).data
    assert _v(data, "user.create.__typename") == "UserCreated"


@skip_db_not_test
def test_user_create_error_already_exist(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_create(name="TestUser")).data
    assert _v(data, "user.create.__typename") == "UserNameAlreadyExistsError"


@skip_db_not_test
def test_user_note_create(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    note_id = _db_note_id("TestNote")
    if note_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(
        user_note_create(user_id=user_id, title="TestNote", content="TestContent")
    ).data
    assert _v(data, "userNote.create.__typename") == "UserNoteCreated"


@skip_db_not_test
def test_user_note_create_error_already_exist(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    note_id = _db_note_id("TestNote")
    if not note_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(
        user_note_create(user_id=user_id, title="TestNote", content="TestContent")
    ).data
    assert _v(data, "userNote.create.__typename") == "UserNoteTitleAlreadyExistsError"


@skip_db_not_test
def test_user_getall(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_getall()).data
    assert _v(data, "user.getAll.users") != []


@skip_db_not_test
def test_user_getone(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_getone(id=user_id)).data
    assert _v(data, "user.getOne.__typename") == "User"


@skip_db_not_test
def test_user_getone_error_not_exists(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_getone(id=-1)).data
    assert data is not None
    assert _v(data, "user.getOne.__typename") == "UserNotExistsError"


@skip_db_not_test
def test_user_note_getall(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    note_id = _db_note_id("TestNote")
    if not note_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_note_getall(user_id=user_id)).data
    assert _v(data, "userNote.getAll.notes") != []


@skip_db_not_test
def test_user_note_getone(async_wait):
    note_id = _db_note_id("TestNote")
    if not note_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_note_getone(id=note_id)).data
    assert _v(data, "userNote.getOne.__typename") == "UserNote"


@skip_db_not_test
def test_user_note_getone_error_not_exists(async_wait):
    data = async_wait(user_note_getone(id=-1)).data
    assert data is not None
    assert _v(data, "userNote.getOne.__typename") == "UserNoteNotExistsError"


@skip_db_not_test
def test_user_note_delete(async_wait):
    note_id = _db_note_id("TestNote")
    if not note_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_note_delete(id=note_id)).data
    assert _v(data, "userNote.delete.__typename") == "UserNoteDeleted"


@skip_db_not_test
def test_user_note_delete_error_not_exists(async_wait):
    data = async_wait(user_note_delete(id=-1)).data
    assert _v(data, "userNote.delete.__typename") == "UserNoteNotExistsError"


@skip_db_not_test
def test_user_delete(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_delete(id=user_id)).data
    assert _v(data, "user.delete.__typename") == "UserDeleted"


@skip_db_not_test
def test_user_delete_error_not_exists(async_wait):
    data = async_wait(user_delete(id=-1)).data
    assert _v(data, "user.delete.__typename") == "UserNotExistsError"
