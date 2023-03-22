class States:
    def __init__(self):
        self.current_state = '*'

    def get_state(self):
        return self.current_state

    def set_creating_state(self):
        self.current_state = 'CREATING_SCENARY'

    def set_using_state(self):
        self.current_state = 'USE_EXIST_SCENARY'

    def set_delete_state(self):
        self.current_state = 'DELETE_SCENARY'
