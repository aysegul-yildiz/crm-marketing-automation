from app.repositories.staff_user_repository import find_staff_by_email


def authenticate_user(email: str, password: str):
  
    staff = find_staff_by_email(email)
    if not staff:
        return None

    if staff.password == password:
        return staff

    return None
