class WorkflowStepModel:
    def __init__(self, id, workflow_id, step_order, action_type, action_payload, status, delay_minutes_after_prev):
        self.id = id
        self.workflow_id = workflow_id
        self.step_order = step_order
        self.action_type = action_type
        self.action_payload = action_payload  # JSON as string/dict
        self.status = status  # 'PENDING' | 'DONE' | 'FAILED'
        self.delay_minutes_after_prev = delay_minutes_after_prev
