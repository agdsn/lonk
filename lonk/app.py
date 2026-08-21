import sys
from os import getenv

import sentry_sdk
from flask import Flask, abort, redirect, render_template, request, url_for
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy.exc import OperationalError

from .db import db
from .lib import (
    create_link,
    get_all_links,
    get_link_count,
    is_valid_url,
    try_lookup_link,
)
from .types_ import FlaskResponse


class Lonk(Flask):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        db_needs_bootstrap = self.init_config()
        db.init_app(self)

        if db_needs_bootstrap:
            with self.app_context():
                db.create_all()

        register_routes(self)
        register_commands(self)

    def init_config(self):
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if uri := getenv('LONK_SQLALCHEMY_DATABASE_URI', None):
            self.config['SQLALCHEMY_DATABASE_URI'] = uri
        if not self.config.get('SQLALCHEMY_DATABASE_URI'):
            self.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
            return True

        return False

def register_routes(app):
    with app.app_context():
        try:
            with app.app_context():
                num_redirects = get_link_count()
        except OperationalError as e:
            print(f"Problem when counting links: {e}.\n"
                  "If you forgot to set up your database schema, please run `flask createdb`.")
            sys.exit()
        if not num_redirects:
            print("Zero redirects sounds like too few. "
                  "Are you sure you remembered to fill your database?")
        else:
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

    @app.route("/_admin", methods=["GET"])
    def admin_overview():
        lonks = get_all_links()

        return render_template('admin.html', lonks=lonks)

    @app.route("/_admin/create", methods=["GET"])
    def create():
        return render_template('create.html')

    @app.route("/_admin/create", methods=["POST"])
    def create_post():
        shortname = request.form.get("shortname", None)
        url = request.form.get("url", None)

        if shortname is None or url is None:
            return render_template('create.html', error='shortname or url missing', shortname=shortname, url=url), 400

        if not is_valid_url(url):
            return render_template('create.html', error='invalid url', shortname=shortname, url=url), 400

        if try_lookup_link(shortname) is not None:
            return render_template('create.html', error='shortname already exists', shortname=shortname, url=url), 400

        create_link(shortname, url)

        return redirect(url_for('admin_overview'))


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
