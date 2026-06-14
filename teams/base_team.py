from abc import ABC
from abc import abstractmethod


class BaseTeam(ABC):

    @abstractmethod
    async def execute(
        self,
        context
    ):
        pass