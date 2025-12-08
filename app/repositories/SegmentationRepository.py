from typing import Optional
from database import get_connection
from app.models.SegmentationRuleModel import SegmentationRuleModel

class SegmentationRepository:

    @staticmethod
    def createSegmentationRule(segmentation_id: int, field: str, operator: str, target_value: str, add_or_remove: bool) -> int:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "INSERT INTO segmentation_rule (segmentation_id, field, operator, target_value, add_or_remove) "
            "VALUES (%s, %s, %s, %s, %s);",
            (segmentation_id, field, operator, target_value, add_or_remove)
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
    