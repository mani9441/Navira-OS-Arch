from runtime.process_context import ProcessContext
from runtime.runtime_result import RuntimeResult


class BaseRuntime:

    
    def __init__(
        self,
        registry,
        resource_manager,
        memory_manager,
        human_manager
    ):
        self.registry = registry
        self.resource_manager = resource_manager
        self.memory_manager = memory_manager
        self.human_manager = human_manager

    async def execute(
        self,
        process_id,
        inputs
    ):
        context = ProcessContext(
            process_id=process_id,
            inputs=inputs,
            resource_manager=self.resource_manager,
            memory_manager=self.memory_manager,
            human_manager=self.human_manager
        )

        try:
            executable = await self.resolve(
                context
            )

            result = await self.run(
                executable,
                context
            )

            return RuntimeResult(
                success=True,
                output=result
            )

        except Exception as e:
            return RuntimeResult(
                success=False,
                error=str(e)
            )

    async def resolve(
        self,
        context
    ):
        raise NotImplementedError()

    async def run(
        self,
        executable,
        context
    ):
        raise NotImplementedError()