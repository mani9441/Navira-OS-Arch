from runtime.base_runtime import (
    BaseRuntime
)
from capabilities.capability_resolver import CapabilityResolver

class CapabilityRuntime(
    BaseRuntime
):

    def __init__(
        self,
        capability_registry,
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

        self.capability_resolver = CapabilityResolver(capability_registry=capability_registry)


    async def resolve(
        self,
        context
    ):
        return await self.capability_resolver.resolve(
            context
        )

    async def run(
        self,
        capability,
        context
    ):
        return await capability.execute(
            context
        )