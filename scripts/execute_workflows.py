import threading
import time
from typing import List
from app.models.WorkflowStepModel import WorkflowStepModel
from app.services.CampaignManagementService import CampaignManagementService


# --- Worker thread ---
def worker(steps: List[WorkflowStepModel]):
    for step in steps:
        try:
            # Execute step
            WorkflowService.execute_step(step)
        except Exception as e:
            step['status'] = 'FAILED'
            print(f"Step {step['id']} failed: {e}")

# --- Main execution ---
def run_workflow_steps_concurrently(all_steps: List[dict], num_threads=4):
    if not all_steps:
        print("No workflow steps to execute.")
        return

    # Split steps into roughly equal chunks for each thread
    chunks = [[] for _ in range(num_threads)]
    for i, step in enumerate(all_steps):
        chunks[i % num_threads].append(step)

    threads = []
    for chunk in chunks:
        if chunk:  # Only start thread if there are steps
            t = threading.Thread(target=worker, args=(chunk,))
            t.start()
            threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print("All threads finished execution.")