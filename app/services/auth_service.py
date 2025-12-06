from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.user_repository import find_by_email, create_user


def register_user(email: str, username: str, password: str):
    password_hash = generate_password_hash(password)
    return create_user(email, username, password_hash)


def authenticate_user(email: str, password: str):
    user = find_by_email(email)
    if not user:
        return None

    if check_password_hash(user.password_hash, password):
        return user

    return None
