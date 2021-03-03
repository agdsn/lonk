import pytest

from lonk.app import app as lonk_app


@pytest.fixture
def app():
    return lonk_app
