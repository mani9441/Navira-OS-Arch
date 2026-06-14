class WorkflowInstance:

    def __init__(
        self,
        workflow,
        context
    ):

        self.workflow = workflow

        self.context = context

    async def execute(self):

        return await self.workflow.execute(
            self.context
        )