from flask import abort, redirect

from .factory import Lonk, check_link_count
from .lib import try_lookup_link
from .types_ import FlaskResponse

app = Lonk(__name__)
check_link_count(app)


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
