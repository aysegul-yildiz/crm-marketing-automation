from functools import wraps
from flask import session, redirect, url_for

def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("email"):
            return redirect(url_for("auth.login"))
        return view(*a, **kw)
    return wrapped
