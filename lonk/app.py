from flask import Flask, redirect

app = Flask("lonk")


@app.route("/")
def index():
    return "Welcome to LONK."


@app.route("/<shortname>")
def resolve_shortlink(shortname: str):
    if shortname == "register":
        return redirect("https://agdsn.de/sipa/register", 301)
    else:
        return f"There is no redirect named '{shortname}'.", 404
    # TODO implement proper redirect from DB


@app.route("/_admin")
def admin_overview():
    # TODO implement admin landing page
    pass


@app.route("/_admin/create", methods=["GET", "POST"])
def create():
    # TODO implement redirect creation
    pass
