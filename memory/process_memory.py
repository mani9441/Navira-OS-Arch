class ProcessMemory:

    def __init__(self):

        self.memories = {}

    def save(
        self,
        process_id,
        data
    ):

        self.memories[
            process_id
        ] = data

    def get(
        self,
        process_id
    ):

        return self.memories.get(
            process_id
        )