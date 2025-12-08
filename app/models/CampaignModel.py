class CampaignModel:
    def __init__(self, id, name, status):
        self.id = id
        self.name = name
        self.status = status  # 'PLANNED' | 'ACTIVE' | 'CLOSED'