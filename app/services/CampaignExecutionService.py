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
        if step.action_type == "email":
            # Send email with relevant payload, send to all users of all segments of this campaign
            groups = CampaignRepository.getSegmentsFromWorkflowStep(step.id)
            body = step.action_payload

            # Use a dictionary to track unique users by their id
            unique_users = {}

            for group in groups:
                customers = SegmentationMaintainerService.fetch_customers(group.id)
                for user in customers:
                    # Key by user.id to avoid duplicates
                    unique_users[user.id] = user

            # Now unique_users.values() contains distinct CustomerModel objects
            for user in unique_users.values():
                # Call your email sender function here
                EmailSenderService.send_email(to=user.email, body=body)
        elif step.action_type == "discord-post":
            #post discord post through webhook
        elif step.action_type == "discount":
            #register discount to segments related to campaign which this workflow belongs
            discount = int(step.action_payload)
            #get relevant segmentation groups
            groups = CampaignRepository.getSegmentsFromWorkflowStep(step.id)
            for group in groups:
                SegmentationRepository.addSegmentationDiscount(group.id, action_payload)

    