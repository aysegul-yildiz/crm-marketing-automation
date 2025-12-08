
class UserEventModel:
    def __init__(self, id, user_id, event_type, event_time, metadata):
        self.id = id
        self.user_id = user_id
        self.event_type = event_type
        self.event_time = event_time
        self.metadata = metadata  # JSON