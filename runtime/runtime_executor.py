import asyncio

from runtime.process import (
    ProcessType,
    ProcessStatus
)


class RuntimeExecutor:

    def __init__(
        self,
        scheduler,
        process_manager,
        kernel,
        capability_runtime,
        workflow_runtime,
        team_runtime,
        planner_runtime=None
    ):
        self.scheduler = scheduler
        self.process_manager = process_manager
        self.kernel = kernel
        self.capability_runtime = capability_runtime
        self.workflow_runtime = workflow_runtime
        self.team_runtime = team_runtime
        self.planner_runtime = planner_runtime
        self.running_tasks = {}

    async def run_forever(self):

        while True:

            process = self.scheduler.dispatch()

            if process:

                task = asyncio.create_task(
                    self._execute_process(
                        process
                    )
                )

                self.running_tasks[
                    process.id
                ] = task

            await asyncio.sleep(
                0.01
            )

    async def _execute_process(
        self,
        process
    ):

        context = process.context

        self.process_manager.update_status(
            process.id,
            ProcessStatus.RUNNING
        )

        try:

            result = await self._execute(
                process,
                context
            )

            await self.kernel.complete_process(
                process.id,
                result=result
            )

            return result

        except Exception as e:

            await self.kernel.fail_process(
                process.id,
                e
            )

        finally:

            self.running_tasks.pop(
                process.id,
                None
            )

    async def _execute(
        self,
        process,
        context
    ):

        raw_inputs = (
            context.inputs
        )

        if process.type == ProcessType.CAPABILITY:

            return await (
                self.capability_runtime.execute(
                    process_id=process.id,
                    inputs=raw_inputs
                )
            )

        if process.type == ProcessType.WORKFLOW:

            return await (
                self.workflow_runtime.execute(
                    process_id=process.id,
                    inputs=raw_inputs
                )
            )

        if process.type == ProcessType.TEAM:

            return await (
                self.team_runtime.execute(
                    process_id=process.id,
                    inputs=raw_inputs
                )
            )

        if (
            process.type ==
            ProcessType.PLANNER
            and
            self.planner_runtime
        ):

            return await (
                self.planner_runtime.execute(
                    process_id=process.id,
                    inputs=raw_inputs
                )
            )

        raise RuntimeError(
            f"Unsupported process "
            f"type {process.type}"
        )