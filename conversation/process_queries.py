class ProcessQueries:

    def __init__(
        self,
        process_manager,
        state_store
    ):

        self.process_manager = (
            process_manager
        )

        self.state_store = (
            state_store
        )

    def process_status(
        self,
        process_id
    ):

        process = (
            self.process_manager.get(
                process_id
            )
        )

        if not process:
            return None

        return {
            "process": process.to_dict(),
            "state": self.state_store.load(
                process_id
            )
        }

    def all_processes(self):

        return [
            p.to_dict()
            for p in self.process_manager.list()
        ]