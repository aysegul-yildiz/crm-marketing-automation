class SegmentationRuleModel:
    def __init__(self, id, segmentation_id, field, operator, target_value, add_or_remove):
        self.id = id
        self.segmentation_id = segmentation_id
        self.field = field
        self.operator = operator
        self.target_value = target_value
        self.add_or_remove = add_or_remove  # boolean