from flask import Flask, redirect, abort

from .lib import try_lookup_link
from .db import db
from .types_ import FlaskResponse


class Lonk(Flask):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
        db.init_app(self)
        register_routes(self)




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


app = Lonk("lonk")
