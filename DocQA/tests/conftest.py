import pytest

from app.documents import store
from app.ratelimit import limiter


@pytest.fixture(autouse=True)
def reset_state():
    store.clear()
    limiter.reset()
    yield
    store.clear()
    limiter.reset()