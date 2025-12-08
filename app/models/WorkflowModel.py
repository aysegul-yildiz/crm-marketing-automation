
class WorkflowModel:
    def __init__(self, id, name, campaign_id, creation_time, execution_start_time):
        self.id = id
        self.name = name
        self.campaign_id = campaign_id
        self.creation_time = creation_time
        self.execution_start_time = execution_start_time