from os import getenv

import sentry_sdk
from flask import Flask, redirect, abort
from sentry_sdk.integrations.flask import FlaskIntegration

from .lib import try_lookup_link
from .db import db
from .types_ import FlaskResponse


class Lonk(Flask):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.init_config()
        db.init_app(self)
        register_routes(self)

    def init_config(self):
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if uri := getenv('LONK_SQLALCHEMY_DATABASE_URI', None):
            self.config['SQLALCHEMY_DATABASE_URI'] = uri
        self.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')


def register_routes(app):
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


# IMPORT-TIME INITIALIZATIONS

if dsn := getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        # release="myapp@1.0.0",
    )


app = Lonk("lonk")
