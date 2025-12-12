import os
import sys

# Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s"
)

import threading
from typing import List
from app.models.WorkflowStepModel import WorkflowStepModel
from app.services.CampaignExecutionService import CampaignExecutionService
from app.services.CampaignManagementService import CampaignManagementService


def worker(steps: List[WorkflowStepModel]):
    for step in steps:
        try:
            logging.info(f"Starting step {step.id} (action={step.action_type})")

            CampaignExecutionService.executeWorkflowStep(step)
            logging.info(f"Finished step {step.id}")
        except Exception as e:
            logging.error(f"Step {step.id} failed: {e}")
            CampaignManagementService.update_workflow_step_status(step.id, "FAILED")



def run_workflow_steps_concurrently(all_steps: List[WorkflowStepModel], num_threads=4):
    print("log1")
    if not all_steps:
        logging.warning("No workflow steps to execute.")
        return

    print("log2")
    chunks = [[] for _ in range(num_threads)]
    for i, step in enumerate(all_steps):
        chunks[i % num_threads].append(step)
    
    logging.info(f"Chunks created: {[len(c) for c in chunks]}")

    threads = []
    for chunk in chunks:
        if chunk:
            t = threading.Thread(target=worker, args=(chunk,))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    logging.info("All threads finished execution.")

if __name__ == "__main__":
    logging.info("Starting workflow executor...")

    # Get workflow steps that need execution
    steps = CampaignManagementService.get_all_next_workflow_steps()

    logging.info(f"Loaded {len(steps)} pending steps.")

    run_workflow_steps_concurrently(steps)

    logging.info("Workflow executor finished.")