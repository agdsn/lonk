from urllib.parse import urlparse

from .db import Redirect, db


def try_lookup_link(shortname: str) -> str | None:
    redirect: Redirect | None
    if not (redirect := db.session.query(Redirect).filter_by(shortname=shortname).one_or_none()):
        return None
    if not is_valid_url(redirect.url):
        return None
    return redirect.url


def is_valid_url(url: str) -> bool:
    try:
        return urlparse(url).scheme in {'http', 'https'}
    except ValueError:
        return False


def get_link_count() -> int:
    return db.session.query(Redirect).count()

def get_all_links() -> list[Redirect]:
    return db.session.query(Redirect).all()

def create_link(shortname: str, url: str) -> None:
    db.session.add(Redirect(shortname=shortname, url=url))
    db.session.commit()
