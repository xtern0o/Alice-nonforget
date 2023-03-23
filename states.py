class States:
    def __init__(self):
        self.scenary = ""
        self.stage = 0

    def set_creating(self, stage: int = 1):
        self.scenary = "CREATING"
        self.stage = stage

    def set_using(self, stage: int = 1):
        self.scenary = "USING"
        self.stage = stage

    def set_delete(self, stage: int = 1):
        self.scenary = "DELETE"
        self.stage = stage

    def set_stage(self, value):
        self.stage = value

    def is_creating(self, stage=None):
        if stage:
            return self.scenary == "CREATING" and self.stage == stage
        return self.scenary == "CREATING" and self.stage

    def is_using(self, stage=None):
        if stage:
            return self.scenary == "USING" and self.stage == stage
        return self.scenary == "USING" and self.stage

    def is_delete(self, stage=None):
        if stage:
            return self.scenary == "DELETE" and self.stage == stage
        return self.scenary == "DELETE" and self.stage

    def get_stage(self):
        return self.stage

    def set_zero(self):
        self.scenary = ""
        self.stage = 0
