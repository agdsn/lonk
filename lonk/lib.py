from typing import Optional
from urllib.parse import urlparse

from .db import db, Redirect


def try_lookup_link(shortname: str) -> Optional[str]:
    if not (url := db.session.query(Redirect).filter_by(shortname=shortname).one_or_none()):
        return None
    if not is_valid_url(url):
        return None
    return url


def is_valid_url(url: str) -> bool:
    try:
        return urlparse(url).scheme in {'http', 'https'}
    except ValueError:
        return False
