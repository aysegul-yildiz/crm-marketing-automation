from typing import Optional
from app.database import get_connection
from app.models.SegmentationRuleModel import SegmentationRuleModel
from app.models.ListingSegmentationModel import ListingSegmentationModel
from app.models.SegmentationGroupModel import SegmentationGroupModel
from app.models.CustomerSegmentationModel import CustomerSegmentationModel
app.models.SegmentationDiscountModel import SegmentationDiscountModel

class SegmentationRepository:

    @staticmethod
    def createSegmentationGroup(name: str) -> int:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "INSERT INTO segmentation_group (name) VALUES(%s);"
        cursor.execute(query, (name,))
        conn.commit()
        segmentation_group_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return segmentation_group_id

    @staticmethod
    def createSegmentationRule(SegmentationRule: SegmentationRuleModel) -> int:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        s = SegmentationRule
        cursor.execute(
            "INSERT INTO segmentation_rule (segmentation_id, field, operator, target_value, add_or_remove) "
            "VALUES (%s, %s, %s, %s, %s);",
            (s.segmentation_id, s.field, s.operator, s.target_value, s.add_or_remove)
        )
        conn.commit()
        rule_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return rule_id

    @staticmethod
    def getSegmentationRuleByID(rule_id: int) -> SegmentationRuleModel | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM segmentation_rule WHERE id = %s;", (rule_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        return SegmentationRuleModel(
            id=row["id"],
            segmentation_id=row["segmentation_id"],
            field=row["field"],
            operator=row["operator"],
            target_value=row["target_value"],
            add_or_remove=row["add_or_remove"]
        )

    @staticmethod
    def addListingToSegment(ListingSegmentation: ListingSegmentationModel):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO listing_segmentation (listing_id, segmentation_id) VALUES (%s, %s);",
            (ListingSegmentation.listing_id, ListingSegmentation.segmentation_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def getSegmentsForListing(listing_id: int) -> list[int]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT segmentation_id FROM listing_segmentation WHERE listing_id = %s;",
            (listing_id,)
        )
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [row[0] for row in rows]
    
    @staticmethod
    def addCustomerToSegment(CustomerSegmentation: CustomerSegmentationModel):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO customer_segmentation (customer_id, segmentation_id) VALUES (%s, %s);",
            (CustomerSegmentation.customer_id, CustomerSegmentation.segmentation_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def getSegmentsForCustomer(customer_id: int) -> list[int]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT segmentation_id FROM user_segmentation WHERE customer_id = %s;",
            (customer_id,)
        )
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [row[0] for row in rows]


    @staticmethod
    def getAllSegmentationGroups() -> list[SegmentationGroupModel]:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT id, name FROM segmentation_group;"
        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [SegmentationGroupModel(id=row[0], name=row[1]) for row in rows]

    @staticmethod
    def getSegmentationDiscount(segmentation_id: int) -> SegmentationDiscountModel | None:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT segmentation_id, discount_percentage
            FROM segmentation_discount
            WHERE segmentation_id = %s;
        """

        cursor.execute(query, (segmentation_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return SegmentationDiscountModel(
                segmentation_id=row[0],
                discount_percentage=row[1]
            )
        return None
        
    @staticmethod
    def addSegmentationDiscount(segmentation_id: int, discount_percentage: int):
        conn = get_connection()
        cursor = conn.cursor()

        # Check if discount already exists for this segmentation group
        existing = CampaignRepository.getSegmentationDiscount(segmentation_id)

        if existing is None:
            # INSERT
            query = """
                INSERT INTO segmentation_discount (segmentation_id, discount_percentage)
                VALUES (%s, %s);
            """
            cursor.execute(query, (segmentation_id, discount_percentage))

        else:
            # UPDATE
            query = """
                UPDATE segmentation_discount
                SET discount_percentage = %s
                WHERE segmentation_id = %s;
            """
            cursor.execute(query, (discount_percentage, segmentation_id))

        conn.commit()
        cursor.close()
        conn.close()
