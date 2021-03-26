from os import getenv

import sentry_sdk
from flask import Flask, redirect, abort
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy.exc import OperationalError

from .lib import get_link_count, try_lookup_link
from .db import db
from .types_ import FlaskResponse


class Lonk(Flask):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.init_config()
        db.init_app(self)
        register_routes(self)
        register_commands(self)

    def init_config(self):
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if uri := getenv('LONK_SQLALCHEMY_DATABASE_URI', None):
            self.config['SQLALCHEMY_DATABASE_URI'] = uri
        if not self.config.get('SQLALCHEMY_DATABASE_URI'):
            self.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
            def _auto_create_db():
                db.create_all()
            self.before_first_request(_auto_create_db)


def register_routes(app):
    @app.before_first_request
    def check_db_connection():
        """Does a sanity check to determine whether the schema has been set up.

        When using a `sqlite://:memory:` db instance, make sure that this hook is registered
        _after_ the auto create function.
        """
        try:
            with app.app_context():
                num_redirects = get_link_count()
        except OperationalError as e:
            print(f"Problem when counting links: {e}.\n"
                  "If you forgot to set up your database schema, please run `flask createdb`.")
            exit()
        print(f"Found {num_redirects} redirects.  Let's go!")

    @app.route("/")
    def index():
        return "Welcome to LONK."

    @app.route("/<shortname>")
    def resolve_shortlink(shortname: str) -> FlaskResponse:
        if not shortname:
            abort(400)

        if url := try_lookup_link(shortname):
            return redirect(url, 301)

        return f"There is no redirect named '{shortname}'.", 404

    @app.route("/_admin")
    def admin_overview():
        # TODO implement admin landing page
        pass

    @app.route("/_admin/create", methods=["GET", "POST"])
    def create():
        # TODO implement redirect creation
        pass


def register_commands(app: Flask):
    @app.cli.command('createdb')
    def create_db():
        db.create_all()


# IMPORT-TIME INITIALIZATIONS

if dsn := getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        # release="myapp@1.0.0",
    )


app = Lonk("lonk")
