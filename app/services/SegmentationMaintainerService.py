from typing import List, Optional

from app.models.SegmentationRuleModel import SegmentationRuleModel
from app.models.ListingSegmentationModel import ListingSegmentationModel
from app.models.SegmentationGroupModel import SegmentationGroupModel
from app.models.CustomerSegmentationModel import CustomerSegmentationModel
from app.models.CustomerModel import CustomerModel
from app.repositories.SegmentationRepository import SegmentationRepository


class SegmentationMaintainerService:

    @staticmethod
    def create_segmentation_group(name: str) -> int:
        if not name:
            raise ValueError("Segmentation group name cannot be empty.")
        return SegmentationRepository.createSegmentationGroup(name)

    @staticmethod
    def create_rule(rule: SegmentationRuleModel) -> int:
        if rule.segmentation_id is None:
            raise ValueError("Segmentation ID must be provided for a rule.")
        if not rule.field or not rule.operator:
            raise ValueError("Field and operator must be provided.")

        return SegmentationRepository.createSegmentationRule(rule)

    @staticmethod
    def get_rule_by_id(rule_id: int) -> Optional[SegmentationRuleModel]:
        return SegmentationRepository.getSegmentationRuleByID(rule_id)

    @staticmethod
    def attach_listing_to_segment(model: ListingSegmentationModel):
        if model.listing_id is None or model.segmentation_id is None:
            raise ValueError("Listing ID and Segmentation ID must be provided.")
        SegmentationRepository.addListingToSegment(model)

    @staticmethod
    def get_segments_for_listing(listing_id: int) -> List[int]:
        return SegmentationRepository.getSegmentsForListing(listing_id)

    @staticmethod
    def attach_customer_to_segment(model: CustomerSegmentationModel):
        if model.customer_id is None or model.segmentation_id is None:
            raise ValueError("Customer ID and Segmentation ID must be provided.")
        
        # Repository implementation currently wrong — this passes correct params
        SegmentationRepository.addCustomerToSegment(model)

    @staticmethod
    def get_segments_for_customer(customer_id: int) -> List[int]:
        return SegmentationRepository.getSegmentsForCustomer(customer_id)

    @staticmethod
    def get_all_groups():
        return SegmentationRepository.getAllSegmentationGroups()

    @staticmethod
    def fetch_customers(segmentation_id: int) -> list[CustomerModel]:
        return SegmentationRepository.get_customers_by_segmentation(segmentation_id)