import sqlite3
from app.models.user import User

DB_PATH = "crm.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def find_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, email, username, password_hash FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if row:
        return User(*row)
    return None


def create_user(email: str, username: str, password_hash: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
            (email, username, password_hash),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
