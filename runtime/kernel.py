from runtime.process import (
    Process,
    ProcessStatus
)
from messaging.events import (
    Event
)

class NaviraKernal:

    def __init__(
        self,
        process_manager,
        scheduler,
        event_manager
    ):
        self.process_manager = process_manager
        self.scheduler = scheduler
        self.event_manager = event_manager

    async def create_process(
        self,
        process_type,
        context=None,
        metadata=None
    ):
        process = Process(
            process_type=process_type,
            metadata=metadata or {}
        )

        process.context = context

        self.process_manager.register(
            process
        )

        await self.event_manager.publish(
            event_type="process.created",
            source=process.id,
            payload={
                "type":
                    process.type.value
            }
        )

        await self.start_process(
            process
        )

        return process
    
    async def start_process(
        self,
        process
    ):
        self.process_manager.update_status(
            process.id,
            ProcessStatus.READY
        )

        self.scheduler.enqueue(
            process
        )

        await self.event_manager.publish(
            event_type="process.ready",
            source=process.id,
            payload={}
        )

        return process
    
    async def pause_process(
        self,
        process_id
    ):
        process = self.process_manager.get(process_id)
        if not process:
            return

        self.process_manager.update_status(
            process_id,
            ProcessStatus.PAUSED
        )

        self.scheduler.pause(process_id)

        # Awaited event emission
        await self.event_manager.publish(
            event_type="process.paused",
            source=process_id,
            payload={}
        )

    async def resume_process(
        self,
        process_id
    ):
        process = self.process_manager.get(process_id)
        if not process:
            return

        self.process_manager.update_status(
            process_id,
            ProcessStatus.READY
        )

        self.scheduler.resume(process_id)

        # Awaited event emission
        await self.event_manager.publish(
            event_type="process.resumed",
            source=process_id,
            payload={}
        )

    async def complete_process(
        self,
        process_id,
        result = None
    ):
        self.process_manager.update_status(
            process_id,
            ProcessStatus.COMPLETED
        )

        # Awaited event emission
        await self.event_manager.publish(
            event_type="process.completed",
            source=process_id,
            payload={
                "result":
                    result
            }
        )

    async def fail_process(
        self,
        process_id,
        error
    ):
        self.process_manager.update_status(
            process_id,
            ProcessStatus.FAILED
        )

        # Awaited event emission
        await self.event_manager.publish(
            event_type="process.failed",
            source=process_id,
            payload={
                "error": str(error)
            }
        )

    async def terminate_process(
        self,
        process_id
    ):
        self.process_manager.remove(process_id)

        # Awaited event emission
        await self.event_manager.publish(
            event_type="process.terminated",
            source=process_id,
            payload={}
        )