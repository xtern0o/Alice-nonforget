class States:
    def __init__(self):
        self.state = "ZERO"
        self.stage = 0

    def set_creating(self, stage: int = 1):
        self.state = "CREATING"
        self.stage = stage

    def set_using(self, stage: int = 1):
        self.state = "USING"
        self.stage = stage

    def set_delete(self, stage: int = 1):
        self.state = "DELETE"
        self.stage = stage

    def set_stage(self, value):
        self.stage = value

    def is_creating(self, stage=None):
        if stage:
            return self.state == "CREATING" and self.stage == stage
        return self.state == "CREATING" and self.stage

    def is_using(self, stage=None):
        if stage:
            return self.state == "USING" and self.stage == stage
        return self.state == "USING" and self.stage

    def is_delete(self, stage=None):
        if stage:
            return self.state == "DELETE" and self.stage == stage
        return self.state == "DELETE" and self.stage

    def get_stage(self):
        return self.stage

    def set_zero(self):
        self.state = "ZERO"
        self.stage = 0
