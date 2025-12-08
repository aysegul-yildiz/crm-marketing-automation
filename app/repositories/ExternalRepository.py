## We will put functions which are not direct parts of MA module in here, for simplicity

from typing import Optional
from database import get_connection
from app.models.CustomerModel import Customer

class ExternalRepository:

    @staticmethod
    def createCustomer(name: str, surname: str, email: str):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Customer (name, surname, email) VALUES (%s, %s, %s);",
            (name, surname, email)
        )
        conn.commit()

        user_id = cursor.lastrowid

        cursor.close()
        conn.close()
    
    @staticmethod
    def getCustomerByID(id: int) -> Customer:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Customer WHERE id = %s;", (id, ))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        return Customer(
            id = row["id"],
            name = row["name"],
            email = row["email"]
        )
        
    @staticmethod
    def createListing(listing_title: str, price: float) -> int:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "INSERT INTO listing (listing_title, price) VALUES (%s, %s);",
            (listing_title, price)
        )
        conn.commit()

        listing_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return listing_id

    @staticmethod
    def getListingByID(listing_id: int) -> ListingModel | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM listing WHERE id = %s;", (listing_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        return ListingModel(
            id=row["id"],
            listing_title=row["listing_title"],
            price=row["price"]
        )