import os
import pytest

os.environ.setdefault('LONK_SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')

@pytest.fixture
def db(app):
    from lonk.db import db

    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
        db.session.commit()
