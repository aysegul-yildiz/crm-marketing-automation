
class CustomerEventModel:
    def __init__(self, id, customer_id, event_type, event_time, metadata):
        self.id = id
        self.customer_id = customer_id
        self.event_type = event_type
        self.event_time = event_time
        self.metadata = metadata  # JSON
