class ProcessContext:

    def __init__(
        self,
        process_id=None,
        inputs=None,
        metadata=None,
        memory_manager=None,
        resource_manager=None,
        human_manager=None
    ):
        self.process_id = process_id
        self.inputs = inputs or {}
        self.metadata = metadata or {}
        self.memory_manager = memory_manager
        self.resource_manager = resource_manager
        self.human_manager = human_manager
        self.state = {}
        self.outputs = {}

    @property
    def query(self):
        return self.inputs.get("query")

    # ─── THE MANDATORY MISSING LINK ───
    def get_input(self, key, default=None):
        """Safely extracts a parameter from the execution context configuration."""
        return self.inputs.get(key, default)

    def set_output(self, key, value):
        self.outputs[key] = value

    def get_output(self, key, default=None):
        return self.outputs.get(key, default)