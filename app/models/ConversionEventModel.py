class ConversionEventModel:
    def __init__(self, id, user_id, listing_id, campaign_id, revenue, occurred_at):
        self.id = id
        self.user_id = user_id
        self.listing_id = listing_id
        self.campaign_id = campaign_id
        self.revenue = revenue
        self.occurred_at = occurred_at