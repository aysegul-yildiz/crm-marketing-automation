from app.database import get_db
from app.models.StaffUserModel import StaffUser

def find_staff_by_email(email: str) -> StaffUser | None:
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, email, password, role FROM StaffUser WHERE email = %s",
        (email,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return StaffUser(**row)
    return None
