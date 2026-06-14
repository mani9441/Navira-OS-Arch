from abc import ABC
from abc import abstractmethod


class BaseWorkflow(ABC):

    @abstractmethod
    async def execute(
        self,
        context
    ):
        pass