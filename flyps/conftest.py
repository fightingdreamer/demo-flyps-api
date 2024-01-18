import asyncio

import pytest

loops = set()


@pytest.fixture
def async_wait():
    loop = asyncio.new_event_loop()
    loops.add(loop)
    yield loop.run_until_complete


def pytest_sessionfinish(session, exitstatus):
    for loop in list(loops):
        loops.remove(loop)
        if not loop.is_running():
            continue
        loop.close()
