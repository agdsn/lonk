import pytest

from lonk.app import app as lonk_app


@pytest.fixture
def app():
    return lonk_app


@pytest.fixture
def db(app):
    from lonk.db import db
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
        db.session.commit()
