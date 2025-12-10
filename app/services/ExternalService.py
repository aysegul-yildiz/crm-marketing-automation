from typing import Optional

from app.models.CustomerModel import Customer
from app.models.ListingModel import ListingModel
from app.repositories.ExternalRepository import ExternalRepository


class ExternalService:

    # ----------------------------------------
    # Customer Operations
    # ----------------------------------------
    @staticmethod
    def create_customer(name: str, surname: str, email: str) -> int:
        if not name or not surname:
            raise ValueError("Customer name and surname cannot be empty.")
        if not email or "@" not in email:
            raise ValueError("A valid email address must be provided.")

        return ExternalRepository.createCustomer(name, surname, email)

    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Customer]:
        if not customer_id or customer_id <= 0:
            raise ValueError("Invalid customer ID.")
        return ExternalRepository.getCustomerByID(customer_id)

    # ----------------------------------------
    # Listing Operations
    # ----------------------------------------
    @staticmethod
    def create_listing(listing_title: str, price: float) -> int:
        if not listing_title:
            raise ValueError("Listing title cannot be empty.")
        if price < 0:
            raise ValueError("Listing price cannot be negative.")

        return ExternalRepository.createListing(listing_title, price)

    @staticmethod
    def get_listing_by_id(listing_id: int) -> Optional[ListingModel]:
        if not listing_id or listing_id <= 0:
            raise ValueError("Invalid listing ID.")
        return ExternalRepository.getListingByID(listing_id)
