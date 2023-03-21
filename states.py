class States:
    def __init__(self):
        self.CREATING_SCENARY = 0
        self.USE_EXIST_SCENARY = 0
        self.DELETE_SCENARY = 0

    def get_creating_state(self):
        return self.CREATING_SCENARY

    def get_using_state(self):
        return self.USE_EXIST_SCENARY

    def get_delete_state(self):
        return self.DELETE_SCENARY

    def set_creating_state(self, value):
        self.CREATING_SCENARY = value

    def set_using_state(self, value):
        self.USE_EXIST_SCENARY = value

    def set_delete_state(self, value):
        self.DELETE_SCENARY = value

