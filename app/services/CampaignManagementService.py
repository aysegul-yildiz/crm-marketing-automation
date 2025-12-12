from __future__ import annotations

from typing import List, Optional

from app.models.CampaignModel import CampaignModel
from app.models.WorkflowModel import WorkflowModel
from app.models.WorkflowStepModel import WorkflowStepModel
from app.repositories.CampaignRepository import CampaignRepository
from app.repositories.SegmentationRepository import SegmentationRepository

class CampaignManagementService:
    @staticmethod
    def create_campaign(name: str, status: str) -> int:
        if not name:
            raise ValueError("Campaign name cannot be empty.")

        return CampaignRepository.createCampaign(name, status)

    @staticmethod
    def get_campaign_by_id(campaign_id: int) -> Optional[CampaignModel]:
        return CampaignRepository.getCampaignByID(campaign_id)

    # ------------------------------
    # Workflow Operations
    # ------------------------------
    @staticmethod
    def create_workflow(name: str, campaign_id: int) -> int:
        if not name:
            raise ValueError("Workflow name cannot be empty.")

        # Additional business logic example:
        # Ensure campaign exists before creating workflow
        campaign = CampaignRepository.getCampaignByID(campaign_id)
        if campaign is None:
            raise ValueError(f"Campaign with ID {campaign_id} does not exist.")

        return CampaignRepository.createWorkflow(name, campaign_id)

    @staticmethod
    def get_workflow_by_id(workflow_id: int) -> Optional[WorkflowModel]:
        return CampaignRepository.getWorkflowByID(workflow_id)

    @staticmethod
    def get_workflows_by_campaign_id(campaign_id: int) -> List[WorkflowModel]:
        return CampaignRepository.getWorkflowsByCampaignID(campaign_id)

    @staticmethod
    def add_workflow_step( workflow_id: int, step_order: int, action_type: str, 
        action_payload, status: str = "PENDING", delay_minutes_after_prev: int = 0) -> int:
        # Verify workflow exists
        wf = CampaignRepository.getWorkflowByID(workflow_id)
        if wf is None:
            raise ValueError(f"Workflow with ID {workflow_id} does not exist.")

        return CampaignRepository.createWorkflowStep(
            workflow_id, step_order, action_type, action_payload, status, delay_minutes_after_prev
        )

    @staticmethod
    def get_workflow_steps(workflow_id: int) -> List[WorkflowStepModel]:
        return CampaignRepository.getWorkflowSteps(workflow_id)

    @staticmethod
    def record_campaign_event(
        customer_id: int,
        campaign_id: int,
        step_id: int,
        event_type: str,
    ) -> int:
        if not event_type:
            raise ValueError("Event type cannot be empty.")

        return CampaignRepository.createCampaignEvent(
            customer_id, campaign_id, step_id, event_type
        )

    @staticmethod
    def get_campaign_events(campaign_id: int):
        return CampaignRepository.getCampaignEvents(campaign_id)

    @staticmethod
    # statusFilter "" empty string for querying everything, else desired status
    def filterCampaigns(statusFilter: str = ""):
        return CampaignRepository.filterCampaigns(statusFilter)

    @staticmethod
    def update_campaign(campaign_id: int, name: str, status: str) -> None:
        if not name:
            raise ValueError("Campaign name cannot be empty.")
        CampaignRepository.updateCampaign(campaign_id, name, status)

    @staticmethod
    def set_segmentation_discount(segmentation_id: int, discount_percentage: int):
        """
        Creates or updates a segmentation group's discount.
        """
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100.")

        return CampaignRepository.addSegmentationDiscount(
            segmentation_id=segmentation_id,
            discount_percentage=discount_percentage
        )

    @staticmethod
    def get_segmentation_discount(segmentation_id: int):
        """
        Fetch segmentation discount model or None.
        """
        return SegmentationRepository.getSegmentationDiscount(segmentation_id)
    @staticmethod
    def update_workflow_step_status(step_id, status):
        CampaignRepository.update_workflow_step_status(step_id, status)

    @staticmethod
    def add_campaign_segment(campaign_id: int, segmentation_id: int):
        CampaignRepository.add_campaign_segment(campaign_id, segmentation_id)

    @staticmethod
    def get_segments_for_campaign(campaign_id: int):
        return CampaignRepository.get_segments_for_campaign(campaign_id)

    @staticmethod
    def get_all_campaigns() -> list:
        return CampaignRepository.get_all_campaigns()

    @staticmethod
    #returns all workflow steps (with status failed or pending), which have the minimum step id in their individual workflows
    def get_all_next_workflow_steps() -> list:
        return CampaignRepository.get_all_next_workflow_steps()