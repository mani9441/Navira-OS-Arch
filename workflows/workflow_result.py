class WorkflowResult:

    def __init__(
        self,
        success,
        output=None,
        error=None
    ):

        self.success = success

        self.output = output

        self.error = error

    def to_dict(self):

        return {
            "success":
                self.success,

            "output":
                self.output,

            "error":
                self.error
        }