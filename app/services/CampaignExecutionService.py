from __future__ import annotations

from typing import List, Optional

from app.models.CampaignModel import CampaignModel
from app.models.WorkflowModel import WorkflowModel
from app.models.WorkflowStepModel import WorkflowStepModel
from app.repositories.CampaignRepository import CampaignRepository
from app.repositories.SegmentationRepository import SegmentationRepository
from app.services.SegmentationMaintainerService import SegmentationMaintainerService
from app.services.email_sender import send_email


class CampaignExecutionService

    # will try and execute the relevant workflow step, no exception handling here
    @staticmethod
    def executeWorkflowStep(step: WorkflowStepModel):
        CHECK(action_type IN ('email', 'discord-post', 'discount')),
        if step.action_type == "email":
            #send email with relevant payload, send to all users of all segments of this campaign
            groups = CampaignRepository.getSegmentsFromWorkflowStep(step.id)
            body = step.action_payload

            users = []
            for group in groups:
                users = SegmentationMaintainerService.fetch_customers(group.id)
                
        elif step.action_type == "discord-post":
            #post discord post through webhook
        elif step.action_type == "discount":
            #register discount to segments related to campaign which this workflow belongs
            discount = int(step.action_payload)
            #get relevant segmentation groups
            groups = CampaignRepository.getSegmentsFromWorkflowStep(step.id)
            for group in groups:
                SegmentationRepository.addSegmentationDiscount(group.id, action_payload)

    