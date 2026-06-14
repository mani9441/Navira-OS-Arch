from processes.base_process import (
    BaseProcess
)

from runtime.process import (
    ProcessStatus
)


class WorkflowProcess(
    BaseProcess
):

    def __init__(
        self,
        process,
        workflow,
        context
    ):

        super().__init__(process)

        self.workflow = workflow

        self.context = context

    async def execute(self):

        result = (
            await self.workflow.run(
                self.context
            )
        )

        self.process.set_status(
            ProcessStatus.COMPLETED
        )

        return result