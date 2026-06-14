class MemoryProvider:

    def __init__(
        self,
        memory_manager
    ):

        self.memory_manager = (
            memory_manager
        )

    def get(self):

        return self.memory_manager