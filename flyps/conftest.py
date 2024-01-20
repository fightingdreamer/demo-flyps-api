import asyncio

import pytest


@pytest.fixture
def async_wait():
    loop = asyncio.new_event_loop()
    yield loop.run_until_complete
    loop.close()
