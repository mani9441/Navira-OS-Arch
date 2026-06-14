class WorkflowContext:

    def __init__(
        self,
        inputs,
        resource_manager,
        memory_manager,
        human_queue
    ):

        self.inputs = inputs

        self.resource_manager = (
            resource_manager
        )

        self.memory_manager = (
            memory_manager
        )

        self.human_queue = (
            human_queue
        )

    def get_input(
        self,
        key,
        default=None
    ):

        return self.inputs.get(
            key,
            default
        )