from runtime.base_runtime import (
    BaseRuntime
)

from workflows.workflow_instance import (
    WorkflowInstance
)

from workflows.workflow_resolver import WorkflowResolver

class WorkflowRuntime(
    BaseRuntime
):

    def __init__(
        self,
        workflow_registry,
        resource_manager,
        memory_manager,
        human_manager
    ):

        super().__init__(
            registry=workflow_registry,
            resource_manager=resource_manager,
            memory_manager=memory_manager,
            human_manager=human_manager
        )

        self.workflow_resolver = WorkflowResolver(workflow_registry)

    async def resolve(
        self,
        context
    ):

        return await self.workflow_resolver.resolve(
            context
        )

    async def run(
        self,
        workflow,
        context
    ):

        instance = WorkflowInstance(
            workflow,
            context
        )

        return await instance.execute()