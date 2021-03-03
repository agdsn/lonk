import pytest
from flask.testing import FlaskClient


def test_root(client: FlaskClient):
    resp = client.get('/')
    assert resp.status_code == 200
    assert "welcome" in resp.data.decode('utf-8').lower()
