from processes.base_process import (
    BaseProcess
)

from runtime.process import (
    ProcessStatus
)


class TeamProcess(
    BaseProcess
):

    def __init__(
        self,
        process,
        team,
        context
    ):

        super().__init__(process)

        self.team = team

        self.context = context

    async def execute(self):

        result = await self.team.run(
            self.context
        )

        self.process.set_status(
            ProcessStatus.COMPLETED
        )

        return result