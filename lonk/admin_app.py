from flask import redirect, render_template, request, url_for

from .factory import Lonk, check_link_count
from .lib import create_link, get_all_links, is_valid_url, try_lookup_link

app = Lonk(__name__)
check_link_count(app)


@app.route("/", methods=["GET"])
def admin_overview():
    lonks = get_all_links()

    return render_template('admin.html', lonks=lonks)


@app.route("/create", methods=["GET"])
def create():
    return render_template('create.html')


@app.route("/create", methods=["POST"])
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
