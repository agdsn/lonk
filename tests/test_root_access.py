from typing import Generator, Any

import pytest
from flask.testing import FlaskClient

from lonk.db import Redirect


@pytest.fixture(autouse=True)
def use_db(db):
    pass


@pytest.fixture(
    params=[
        ("register", "https://agdsn.de/sipa/register"),
        ("ggl", "http://google.de"),
        ("lh", "https://localhost:1432"),
    ],
    ids=["sipa", "google", "localhost"],
)
def redirect(db, request) -> Generator[Redirect, Any, Any]:
    shortname, url = request.param
    redirect = Redirect(shortname=shortname, url=url)
    db.session.add(redirect)
    db.session.commit()
    yield redirect
    db.session.delete(redirect)
    db.session.commit()


def test_root(client: FlaskClient):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "welcome" in resp.data.decode("utf-8").lower()


@pytest.mark.parametrize("url", ["foo", "bar", "Hans", "Peter", "nonexistent"])
def test_nonexistent_redirect(client: FlaskClient, url):
    resp = client.get(f"/{url}")
    assert resp.status_code == 404
    assert "there is no redirect" in resp.data.decode("utf-8").lower()


def test_existent_redirect(redirect: Redirect, client: FlaskClient):
    resp = client.get(f"/{redirect.shortname}")
    assert resp.status_code == 301  # Moved permanently
    assert resp.location == redirect.url
