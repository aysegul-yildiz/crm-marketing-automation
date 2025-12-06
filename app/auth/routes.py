import os
import secrets
import time
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

# users.txt and tokens.txt will live one level above this file (inside app/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "..", "users.txt")
TOKENS_FILE = os.path.join(BASE_DIR, "..", "tokens.txt")


# ---------- helpers ----------
def _line_parts(line: str):
    return [p.strip() for p in line.strip().split(",")]


def read_users():
    users = {}
    if not os.path.exists(USERS_FILE):
        return users
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = _line_parts(line)
            if len(parts) == 3:
                email, username, password_or_hash = parts
            else:
                continue
            users[email] = {"username": username, "pw": password_or_hash}
    return users


def write_user(email: str, username: str, pw_hash: str) -> bool:
    users = read_users()
    if email in users:
        return False
    with open(USERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{email},{username},{pw_hash}\n")
    return True


def _rewrite_users(users_dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for email, u in users_dict.items():
            f.write(f"{email},{u['username']},{u['pw']}\n")


def is_hash(value: str) -> bool:
    return value.startswith("pbkdf2:sha256:") or value.startswith("scrypt:")


def save_token(token, email, exp):
    with open(TOKENS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{token},{email},{int(exp)}\n")


def read_tokens():
    tokens = {}
    if not os.path.exists(TOKENS_FILE):
        return tokens
    now = int(time.time())
    with open(TOKENS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = _line_parts(line)
            if len(parts) < 3:
                continue
            token, email, exp = parts[:3]
            if now <= int(exp):
                tokens[token] = {"email": email, "exp": int(exp)}
    return tokens


def _require_bearer(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    return read_tokens().get(token)


# ---------- decorator used by other modules ----------
def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("email"):
            return redirect(url_for("auth.login"))
        return view(*a, **kw)

    return wrapped


# ---------- routes ----------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        users = read_users()
        u = users.get(email)

        if not u:
            return "Invalid credentials. <a href='/login'>Try again</a>"

        stored = u["pw"]
        ok = check_password_hash(stored, password) if is_hash(stored) else (
            stored == password
        )

        if ok:
            if not is_hash(stored):
                new_hash = generate_password_hash(password)
                users[email]["pw"] = new_hash
                _rewrite_users(users)

            session["email"] = email
            session["username"] = u["username"]
            return redirect(url_for("marketing.dashboard"))
        else:
            return "Invalid credentials. <a href='/login'>Try again</a>"

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_again = request.form.get("passwordAgain", "")

        if "," in password or "," in email or "," in username:
            return "Fields cannot contain commas. Please go back and try again.", 400
        if password != password_again:
            return "Passwords do not match. Please go back and try again.", 400

        pw_hash = generate_password_hash(password)
        res = write_user(email, username, pw_hash)
        if res:
            return "Registered successfully! <a href='/login'>Login here</a>"
        else:
            return "Email already registered <a href='/register'>Try again</a>"

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# optional API token endpoint, keep only if you need it
@auth_bp.post("/api/v1/auth/token")
def api_issue_token():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    users = read_users()
    u = users.get(email)
    if not u:
        return jsonify({"error": "unauthorized"}), 401
    stored = u["pw"]
    ok = check_password_hash(stored, password) if is_hash(stored) else (
        stored == password
    )
    if not ok:
        return jsonify({"error": "unauthorized"}), 401
    token = secrets.token_urlsafe(32)
    exp = int(time.time()) + 3600
    save_token(token, email, exp)
    return jsonify({"token": token, "exp": exp})
