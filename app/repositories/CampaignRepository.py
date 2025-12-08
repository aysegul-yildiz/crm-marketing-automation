from app.database import get_connection
from app.models.campaign_model import CampaignModel

class CampaignRepository:

    @staticmethod
    def createCampaign(name: str, status: str) -> int:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "INSERT INTO campaign (name, status) VALUES (%s, %s);",
            (name, status)
        )
        conn.commit()
        campaign_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return campaign_id

    @staticmethod
    def getCampaignByID(campaign_id: int) -> CampaignModel | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM campaign WHERE id = %s;", (campaign_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        return CampaignModel(
            id=row["id"],
            name=row["name"],
            status=row["status"]
        )
