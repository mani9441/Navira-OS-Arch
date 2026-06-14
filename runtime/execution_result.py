class ExecutionResult:

    def __init__(
        self,
        success,
        process_id=None,
        error=None
    ):

        self.success = success

        self.process_id = (
            process_id
        )

        self.error = error

    def to_dict(self):

        return {

            "success":
                self.success,

            "process_id":
                self.process_id,

            "error":
                self.error
        }