class CampaignEventModel:
    def __init__(self, id, user_id, campaign_id, step_id, event_type, event_time):
        self.id = id
        self.user_id = user_id
        self.campaign_id = campaign_id
        self.step_id = step_id
        self.event_type = event_type
        self.event_time = event_time