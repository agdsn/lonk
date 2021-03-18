from typing import Optional
from urllib.parse import urlparse

from .db import db, Redirect


def try_lookup_link(shortname: str) -> Optional[str]:
    redirect: Optional[Redirect]
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
