from app.database import get_connection
from app.models.CampaignModel import CampaignModel
from app.models.WorkflowStepModel import WorkflowStepModel

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

    @staticmethod
    def createWorkflowStep(workflow_id: int, step_order: int,
               action_type: str, action_payload, status: str = "PENDING") -> int:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO workflow_step (workflow_id, step_order, action_type, action_payload, status)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (workflow_id, step_order, action_type, action_payload, status))
        conn.commit()

        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id

    @staticmethod
    #returns array of WorkflowStepModel, in ascending step order
    def getWorkflowSteps(workflow_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT *
        FROM workflow_step
        WHERE workflow_id = %s
        ORDER BY step_order ASC;
        """
        cursor.execute(query, (workflow_id,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        result = []

        for(r in rows):
            model = WorkflowStepModel(
                id = r["id"],
                workflow_id = r["workflow_id"],
                step_order = r["step_order"],
                action_type = r["action_type"],
                action_payload = r["action_payload"],
                status = r["status"]
            )
            result.append(model)

        return result

    @staticmethod
    def createCampaignEvent(customer_id: int, campaign_id: int, step_id: int, event_type: str) -> int:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO campaign_event (customer_id, campaign_id, step_id, event_type)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (customer_id, campaign_id, step_id, event_type))
        conn.commit()

        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id

    @staticmethod
    def getCampaignEvents(campaign_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT *
        FROM campaign_event
        WHERE campaign_id = %s
        ORDER BY event_time DESC;
        """
        cursor.execute(query, (campaign_id,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return rows