import pytest

from flyps import db
from flyps.graphql import schema
from flyps.model import UserNoteTable, UserTable
from flyps.util.operator import itempathgetter

# ------------------------------------------------------------------------------


async def get_users():
    return await schema.execute(
        """
        query getUsers {
            getUsers {
                ... on Users {
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


async def get_user(*, id: int):
    return await schema.execute(
        """
        query getUser($id: ID!) {
            getUser(id: $id) {
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
        """,
        variable_values={"id": id},
    )


async def user_create(*, name: str):
    return await schema.execute(
        """
        mutation userCreate($name: String!) {
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


async def user_delete(*, id: int):
    return await schema.execute(
        """
        mutation userDelete($id: ID!) {
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


async def get_user_notes(*, user_id: int):
    return await schema.execute(
        """
        query getUserNotes($userId: ID!) {
            getUserNotes(userId: $userId) {
                __typename
                ... on UserNotExistsError {
                    id
                }
                ... on UserNotes {
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


async def get_user_note(*, id: int):
    return await schema.execute(
        """
        query getUserNote($id: ID!) {
            getUserNote(id: $id) {
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
        """,
        variable_values={"id": id},
    )


async def user_note_create(*, user_id: int, title: str, content: str):
    return await schema.execute(
        """
        mutation userNoteCreate($userId: ID!, $title: String!, $content: String!) {
            user {
                note {
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
        }
        """,
        variable_values={
            "title": title,
            "userId": user_id,
            "content": content,
        },
    )


async def user_note_delete(*, id: int):
    return await schema.execute(
        """
        mutation userNoteDelete($id: ID!) {
            user {
                note {
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


skip_db_not_test = pytest.mark.xfail(
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
    assert _v(data, "user.note.create.__typename") == "UserNoteCreated"


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
    assert _v(data, "user.note.create.__typename") == "UserNoteTitleAlreadyExistsError"


@skip_db_not_test
def test_get_users(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(get_users()).data
    assert _v(data, "getUsers.users") != []


@skip_db_not_test
def test_get_user(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(get_user(id=user_id)).data
    assert _v(data, "getUser.__typename") == "User"


@skip_db_not_test
def test_get_user_error_not_exists(async_wait):
    data = async_wait(get_user(id=-1)).data
    assert data is not None
    assert _v(data, "getUser.__typename") == "UserNotExistsError"


@skip_db_not_test
def test_get_user_notes(async_wait):
    user_id = _db_user_id("TestUser")
    if not user_id:  # pragma: no cover
        pytest.skip()

    note_id = _db_note_id("TestNote")
    if not note_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(get_user_notes(user_id=user_id)).data
    assert _v(data, "getUserNotes.notes") != []


@skip_db_not_test
def test_get_user_notes_error_not_exists(async_wait):
    data = async_wait(get_user_notes(user_id=-1)).data
    assert _v(data, "getUserNotes.__typename") == "UserNotExistsError"


@skip_db_not_test
def test_get_user_note(async_wait):
    note_id = _db_note_id("TestNote")
    if not note_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(get_user_note(id=note_id)).data
    assert _v(data, "getUserNote.__typename") == "UserNote"


@skip_db_not_test
def test_test_user_note_error_note_not_exists(async_wait):
    data = async_wait(get_user_note(id=-1)).data
    assert data is not None
    assert _v(data, "getUserNote.__typename") == "UserNoteNotExistsError"


@skip_db_not_test
def test_user_note_delete(async_wait):
    note_id = _db_note_id("TestNote")
    if not note_id:  # pragma: no cover
        pytest.skip()

    data = async_wait(user_note_delete(id=note_id)).data
    assert _v(data, "user.note.delete.__typename") == "UserNoteDeleted"


@skip_db_not_test
def test_user_note_delete_error_not_exists(async_wait):
    data = async_wait(user_note_delete(id=-1)).data
    assert _v(data, "user.note.delete.__typename") == "UserNoteNotExistsError"


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
