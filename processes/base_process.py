from abc import ABC
from abc import abstractmethod

from runtime.process import Process
from runtime.process import ProcessStatus


class BaseProcess(ABC):

    def __init__(
        self,
        process: Process
    ):

        self.process = process

    async def start(self):

        self.process.set_status(
            ProcessStatus.RUNNING
        )

        return await self.execute()

    async def pause(self):

        self.process.set_status(
            ProcessStatus.WAITING
        )

    async def terminate(self):

        self.process.set_status(
            ProcessStatus.TERMINATED
        )

    @abstractmethod
    async def execute(self):
        pass