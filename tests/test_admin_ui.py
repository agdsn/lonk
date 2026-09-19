import pytest
from flask.testing import FlaskClient
import os

overview_page = '/'
create_page = '/create'

@pytest.fixture
def app():
    from lonk.admin_app import app as admin_app
    return admin_app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def use_db(db):
    pass


def test_overview(client: FlaskClient):
    resp = client.get(overview_page)
    assert resp.status_code == 200

    content_lower = resp.data.decode('utf-8').lower()

    assert 'existing redirects' in content_lower
    assert 'create new link' in content_lower
    assert f'href="{create_page}"' in content_lower
    

def test_create_get(client: FlaskClient):
    resp = client.get(create_page)
    assert resp.status_code == 200

    content_lower = resp.data.decode('utf-8').lower()

    assert 'shortname:' in content_lower
    assert '<input type="text" id="shortname"' in content_lower
    assert 'url:' in content_lower
    assert '<input type="text" id="url"' in content_lower

@pytest.mark.parametrize("redirect", [
    ('wichtig', 'https://tud.link/45kc'),
    ('lustig', 'https://go.agdsn.de/telefonie'),
])
def test_create_post_success(client: FlaskClient, redirect: set[str, str]):
    shortname, url = redirect
    resp = client.post(create_page, data={'shortname': shortname, 'url': url})
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/'

    get_resp = client.get(overview_page)
    assert get_resp.status_code == 200

    content = get_resp.data.decode('utf-8')

    assert f'<td>{shortname}</td>' in content
    assert f'<td><a href="{url}">{url}</a></td>' in content


def test_create_post_fail_missing(client: FlaskClient):
    resp = client.post(create_page)
    assert resp.status_code == 400

    assert 'error: ' in resp.data.decode('utf-8').lower()


@pytest.mark.parametrize("data", [('shortname', 'lustig'),
                                      ('url', 'https://tud.link/45kc')])
def test_create_post_fail_missing(client: FlaskClient, data: set[str, str]):
    key, value = data
    resp = client.post(create_page, data={key: value})
    assert resp.status_code == 400

    assert 'error: shortname or url missing' in resp.data.decode('utf-8').lower()


@pytest.mark.parametrize("redirect", [('wichtig', 'htps://tud.link/45kc'),
                                      ('lustig', 'go.agdsn.de/telefonie')])
def test_create_post_fail_invalid_url(client: FlaskClient, redirect: set[str, str]):
    shortname, url = redirect
    resp = client.post(create_page, data={'shortname': shortname, 'url': url})
    assert resp.status_code == 400

    assert 'error: invalid url' in resp.data.decode('utf-8').lower()


@pytest.mark.parametrize("redirect", [('wichtig', 'https://tud.link/45kc'),
                                      ('lustig', 'https://go.agdsn.de/telefonie')])
def test_create_post_fail_already_exists(client: FlaskClient, redirect: set[str, str]):
    shortname, url = redirect
    first_resp = client.post(create_page, data={'shortname': shortname, 'url': url})
    assert first_resp.status_code == 302

    resp = client.post(create_page, data={'shortname': shortname, 'url': url})
    assert resp.status_code == 400

    assert 'shortname already exists' in resp.data.decode('utf-8').lower()




