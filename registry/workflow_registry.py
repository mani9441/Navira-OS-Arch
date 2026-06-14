class WorkflowRegistry:

    def __init__(self):

        self.workflows = {}

    def register(
        self,
        name,
        workflow
    ):

        self.workflows[name] = workflow

    def get(self, name):

        return self.workflows.get(name)

    def list(self):

        return list(
            self.workflows.keys()
        )