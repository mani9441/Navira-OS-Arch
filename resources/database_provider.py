class DatabaseProvider:

    def __init__(self):

        self.databases = {}

    def register(
        self,
        name,
        database
    ):

        self.databases[
            name
        ] = database

    def get(
        self,
        name
    ):

        return self.databases.get(
            name
        )