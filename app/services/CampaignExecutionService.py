from __future__ import annotations
import json


from typing import List, Optional

from app.models.CampaignModel import CampaignModel
from app.models.WorkflowModel import WorkflowModel
from app.models.WorkflowStepModel import WorkflowStepModel
from app.repositories.CampaignRepository import CampaignRepository
from app.repositories.SegmentationRepository import SegmentationRepository
from app.services.SegmentationMaintainerService import SegmentationMaintainerService
from app.services.DiscordSenderService import DiscordSenderService
from app.services.email_sender import send_email
from app.services.CampaignManagementService import CampaignManagementService



class CampaignExecutionService:

    # will try and execute the relevant workflow step, no exception handling here
    @staticmethod
    def executeWorkflowStep(step: WorkflowStepModel):
        try:
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
                    send_email(to_email=user.email, subject="crm marketing notification", 
                        body=body, from_email="yourmail@outlook.com", smtp_server="smtp.office365.com", smtp_port=587, username="yourmail@outlook.com", password="yourpassword")
            elif step.action_type == "discord-post":
                #post discord post through webhook
                raw_text = step.action_payload
                message = raw_text.strip().strip('"').strip("'") #strip quotes

                webhook_url = "https://discord.com/api/webhooks/1447853640973815808/AnJs6zy3YAK74v39N38TyNPx6veIo5MvMWrAejoiwfxAynBSHXQOqSQMENzMmR3xkUaZ"
                if message and webhook_url:
                    DiscordSenderService.send_discord_post(webhook_url, message)
            elif step.action_type == "discount":
                #register discount to segments related to campaign which this workflow belongs
                discount = int(step.action_payload)
                #get relevant segmentation groups
                groups = CampaignRepository.getSegmentsFromWorkflowStep(step.id)
                for group in groups:
                    SegmentationRepository.addSegmentationDiscount(group.id, discount)

            CampaignManagementService.update_workflow_step_status(step.id, "DONE")

        except Exception as e:
            # Catch any exception, log it, and mark step as failed
            print(f"Workflow step {step.id} failed: {e}")
            CampaignManagementService.update_workflow_step_status(step.id, "FAILED")