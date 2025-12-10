# app/repositories/CampaignRepository.py
from __future__ import annotations

import json
from typing import List, Optional

from app.database import get_connection
from app.models.CampaignModel import CampaignModel
from app.models.WorkflowStepModel import WorkflowStepModel
from app.models.WorkflowModel import WorkflowModel


class CampaignRepository:
    @staticmethod
    def createCampaign(name: str, status: str) -> int:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "INSERT INTO campaign (name, status) VALUES (%s, %s);",
            (name, status),
        )
        conn.commit()
        campaign_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return campaign_id

    @staticmethod
    def getCampaignByID(campaign_id: int) -> Optional[CampaignModel]:
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
            status=row["status"],
        )

    @staticmethod
    def createWorkflow(name: str, campaign_id: int) -> int:
        conn = get_connection()
        cursor = conn.cursor()

        query = "INSERT INTO workflow (name, campaign_id) VALUES (%s, %s);"
        cursor.execute(query, (name, campaign_id))
        conn.commit()

        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id

    @staticmethod
    def getWorkflowByID(workflow_id: int) -> Optional[WorkflowModel]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM workflow WHERE id = %s;"
        cursor.execute(query, (workflow_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        return WorkflowModel(
            id=row["id"],
            name=row["name"],
            campaign_id=row["campaign_id"],
            creation_time=row["creation_time"],
            execution_start_time=row["execution_start_time"],
        )

    @staticmethod
    def getWorkflowsByCampaignID(campaign_id: int) -> List[WorkflowModel]:
        """
        Returns all workflows for a campaign.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM workflow WHERE campaign_id = %s;"
        cursor.execute(query, (campaign_id,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        result: List[WorkflowModel] = []
        for row in rows:
            result.append(
                WorkflowModel(
                    id=row["id"],
                    name=row["name"],
                    campaign_id=row["campaign_id"],
                    creation_time=row["creation_time"],
                    execution_start_time=row["execution_start_time"],
                )
            )
        return result

    @staticmethod
    def createWorkflowStep(
        workflow_id: int,
        step_order: int,
        action_type: str,
        action_payload,
        status: str = "PENDING",
    ) -> int:
        conn = get_connection()
        cursor = conn.cursor()

        # store payload as JSON string
        payload_str = json.dumps(action_payload) if action_payload is not None else None

        query = """
            INSERT INTO workflow_step (
                workflow_id, step_order, action_type, action_payload, status
            )
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(
            query, (workflow_id, step_order, action_type, payload_str, status)
        )
        conn.commit()

        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return new_id

    @staticmethod
    def getWorkflowSteps(workflow_id: int) -> list[WorkflowStepModel]:
        """
        Returns all steps for a workflow in ascending step_order.
        """
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

        result: list[WorkflowStepModel] = []
        for r in rows:
            payload = r["action_payload"]
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except Exception:
                    pass

            result.append(
                WorkflowStepModel(
                    id=r["id"],
                    workflow_id=r["workflow_id"],
                    step_order=r["step_order"],
                    action_type=r["action_type"],
                    action_payload=payload,
                    status=r["status"],
                )
            )

        return result

    @staticmethod
    def createCampaignEvent(
        customer_id: int,
        campaign_id: int,
        step_id: int,
        event_type: str,
    ) -> int:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO campaign_event (
                customer_id, campaign_id, step_id, event_type
            )
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

    @staticmethod
    # statusFilter "" empty string for querying everything, else desired status
    def filterCampaigns(statusFilter: str = ""):
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)

        
        if statusFilter == "":
            query = "SELECT * FROM campaign ORDER BY id DESC;"
            cursor.execute(query)
        else:
            query = "SELECT * FROM campaign WHERE status = %s ORDER BY id DESC;"
            cursor.execute(query, (statusFilter, ))
        
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        result = []
        for row in rows:
            model = CampaignModel(
                id=row["id"],
                name=row["name"],
                status=row["status"],
            )
            result.append(model)
        
        return result
    
    @staticmethod
    def updateCampaign(campaign_id: int, name: str, status: str) -> None:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            UPDATE campaign
            SET name = %s, status = %s
            WHERE id = %s
        """
        cur.execute(query, (name, status, campaign_id))
        conn.commit()
        cur.close()
        conn.close()
