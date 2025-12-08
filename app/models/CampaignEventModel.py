class CampaignEventModel:
    def __init__(self, id, customer_id, campaign_id, step_id, event_type, event_time):
        self.id = id
        self.customer_id = customer_id
        self.campaign_id = campaign_id
        self.step_id = step_id
        self.event_type = event_type
        self.event_time = event_time
