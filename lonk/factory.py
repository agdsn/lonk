import sys
from os import getenv

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import StaticPool
from pathlib import Path


from .db import db
from .lib import get_link_count
import os

class Lonk(Flask):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        create = self.init_config()
        db.init_app(self)
        if create or os.environ.get("LONK_CREAT_SCHEMA", "flase" == "true"):
            with self.app_context():
                db.create_all()

        register_commands(self)

    def init_config(self):
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        create = False
        if uri := getenv('LONK_SQLALCHEMY_DATABASE_URI', None):
            self.config['SQLALCHEMY_DATABASE_URI'] = uri
            if is_sqlite_memory_uri(uri):
                # An in-memory database starts out empty every time and is
                # gone once the connection closes, so it must be recreated
                # on startup, and all connections must share a single pool
                # or each one gets its own empty database.
                create = True
                self.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                    'poolclass': StaticPool,
                    'connect_args': {'check_same_thread': False},
                }
        else:
            if not os.path.exists('data/lonk.db'):
                create = True
                Path('data/lonk.db').touch(exist_ok=False)

            self.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{ os.getcwd() }/data/lonk.db'
        return create


def is_sqlite_memory_uri(uri: str) -> bool:
    return uri.startswith('sqlite://') and (uri in ('sqlite://', 'sqlite:///:memory:') or ':memory:' in uri)


def register_commands(app: Flask):
    @app.cli.command('createdb')
    def create_db():
        db.create_all()


def check_link_count(app: Flask) -> None:
    """Init-time sanity check, run once by each app module right after it's created.

    Skipped when `flask createdb` is the command being run, since that's a
    maintenance command, not app startup.
    """
    if 'createdb' in sys.argv:
        return

    with app.app_context():
        try:
            num_redirects = get_link_count()
        except OperationalError as e:
            app.logger.error(f"Problem when counting links: {e}.\n"
                            "If you forgot to set up your database schema, please run `flask createdb`.")
            sys.exit(1)
        if not num_redirects:
            app.logger.warning("Zero redirects sounds like too few. "
                                "Are you sure you remembered to fill your database?")
        else:
            app.logger.info(f"Found {num_redirects} redirects.  Let's go!")


if dsn := getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        # release="myapp@1.0.0",
    )
