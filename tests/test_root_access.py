import pytest
from flask.testing import FlaskClient


def test_root(client: FlaskClient):
    resp = client.get('/')
    assert resp.status_code == 200
    assert "welcome" in resp.data.decode('utf-8').lower()


@pytest.mark.parametrize("url", ['foo', 'bar', 'Hans', 'Peter', 'nonexistent'])
def test_nonexistent_redirect(client: FlaskClient, url):
    resp = client.get(f"/{url}")
    assert resp.status_code == 404
    assert "there is no redirect" in resp.data.decode('utf-8').lower()


def test_existent_redirect(client: FlaskClient):
    resp = client.get(f"/register")
    assert resp.status_code == 301  # Moved permanently
    assert resp.location == "https://agdsn.de/sipa/register"
