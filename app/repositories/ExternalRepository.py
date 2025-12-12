## We will put functions which are not direct parts of MA module in here, for simplicity

from typing import Optional
from app.database import get_connection
from app.models.CustomerModel import CustomerModel
from app.models.ListingModel import ListingModel

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
    def getCustomerByID(id: int) -> CustomerModel:
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)

        cursor.execute("SELECT * FROM Customer WHERE id = %s;", (id, ))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        return CustomerModel(
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

    @staticmethod
    def getAllCustomers() -> list[CustomerModel]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Customer;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        customers = []
        for r in rows:
            customers.append(CustomerModel(
                id=r["id"],
                name=r["name"],
                surname=r["surname"],
                email=r["email"]
            ))
        return customers

    @staticmethod
    def getAllListings() -> list[ListingModel]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM listing;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        listings = []
        for r in rows:
            listings.append(ListingModel(
                id=r["id"],
                listing_title=r["listing_title"],
                price=r["price"]
            ))
        return listings
