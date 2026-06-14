from processes.base_process import (
    BaseProcess
)

from runtime.process import (
    ProcessStatus
)


class CapabilityProcess(
    BaseProcess
):

    def __init__(
        self,
        process,
        capability,
        context
    ):

        super().__init__(process)

        self.capability = capability

        self.context = context

    async def execute(self):

        try:

            result = (
                await self.capability.execute(
                    self.context
                )
            )

            self.process.set_status(
                ProcessStatus.COMPLETED
            )

            return result

        except Exception:

            self.process.set_status(
                ProcessStatus.FAILED
            )

            raise