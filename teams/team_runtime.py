from runtime.base_runtime import (
    BaseRuntime
)

from teams.team_instance import (
    TeamInstance
)

from teams.team_resolver import TeamResolver

class TeamRuntime(
    BaseRuntime
):

    def __init__(
        self,
        team_registry,
        resource_manager,
        memory_manager,
        human_manager
    ):
        super().__init__(
            registry=None,
            resource_manager=resource_manager,
            memory_manager=memory_manager,
            human_manager=human_manager
        )

        self.team_resolver = TeamResolver(team_registry)

    async def resolve(
        self,
        context
    ):
        return await self.team_resolver.resolve(
            context
        )

    async def run(
        self,
        team,
        context
    ):

        instance = TeamInstance(
            team,
            context
        )

        return await instance.execute()