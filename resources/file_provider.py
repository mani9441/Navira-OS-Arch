class FileProvider:

    def __init__(self):

        self.files = {}

    def register(
        self,
        file_id,
        file_object
    ):

        self.files[
            file_id
        ] = file_object

    def get(
        self,
        file_id
    ):

        return self.files.get(
            file_id
        )