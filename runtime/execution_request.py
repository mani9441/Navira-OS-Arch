class ExecutionRequest:

    def __init__(
        self,
        process_type,
        inputs=None,
        metadata=None
    ):


        self.process_type = (
            process_type
        )

        self.inputs = (
            inputs or {}
        )

        self.metadata = (
            metadata or {}
        )