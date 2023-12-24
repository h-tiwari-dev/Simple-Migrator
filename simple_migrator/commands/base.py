class BaseCommand:
    def __init__(self, database):
        self.database = database

    def get_query(self):
        raise NotImplementedError("Subclasses must implement the execute method.")
