from processes.base_process import (
    BaseProcess
)

from runtime.process import (
    ProcessStatus
)


class PlannerProcess(
    BaseProcess
):

    async def execute(self):

        self.process.set_status(
            ProcessStatus.COMPLETED
        )

        return {
            "planner": "not implemented"
        }