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
        event_manager,
        capability_runtime=None,
        workflow_runtime=None,
        team_runtime=None
    ):
        self.process_manager = process_manager
        self.scheduler = scheduler
        self.event_manager = event_manager
        
        self.capability_runtime = capability_runtime
        self.workflow_runtime = workflow_runtime
        self.team_runtime = team_runtime

        # ─── THE SYSTEM GLUE: AUTOMATIC SUBSCRIPTIONS ───
        self.event_manager.subscribe("human.requested", self._on_human_requested)
        self.event_manager.subscribe("human.responded", self._on_human_responded)

    # ─── AUTOMATIC STATE TRANSITION 1: MOVE TO WAIT ───
    async def _on_human_requested(self, event):
        """
        Triggered automatically whenever a runtime calls human_manager.ask().
        The kernel shifts the process out of RUNNING into the WAITING queue.
        """
        process_id = event.source
        
        self.process_manager.update_status(process_id, ProcessStatus.WAITING)
        self.scheduler.wait(process_id)

    # ─── AUTOMATIC STATE TRANSITION 2: INTERCEPT AND EVALUATE DATA ───
    async def _on_human_responded(self, event):
        """
        Triggered automatically when your multi-screen API calls human_manager.respond().
        Routes the data payload to the correct runtime module to save state to disk,
        then updates the core OS process lifecycles.
        """
        process_id = event.source
        response_value = event.payload.get("response")

        process = self.process_manager.get(process_id)
        if not process:
            return

        step_result = {"status": "running"}  # Fallback state

        # 1. Route response data payload to the active tracking runtime instance
        if process.type.value == "capability" and self.capability_runtime:
            try:
                # Modifies file tracking state securely on disk
                step_result = await self.capability_runtime.resume(
                    process_id=process_id,
                    response=response_value,
                    context=process.context
                )
            except ValueError:
                pass
                
        elif process.type.value == "workflow" and self.workflow_runtime:
            try:
                step_result = await self.workflow_runtime.resume(
                    process_id=process_id,
                    response=response_value,
                    context=process.context
                )
            except ValueError:
                pass

        # 2. Coordinate Kernel state based on what the runtime returned
        if step_result.get("status") == "completed":
            await self.complete_process(process_id, result=step_result.get("result"))
            self.scheduler.mark_completed(process_id)
            
        elif step_result.get("status") == "waiting":
            # The runtime file updated, but it is waiting on another missing field.
            # Leave the process resting in the waiting queue.
            pass
            
        else:
            # ─── FIXED ───
            # Call your explicit resume_process method to handle thread safety!
            # It updates process status, wakes the scheduler queue, and publishes events.
            await self.resume_process(process_id)

    # ─── CORE OS LIFECYCLE MANAGEMENT METHODS ───

    async def create_process(self, process_type, context=None, metadata=None):
        process = Process(process_type=process_type, metadata=metadata or {})
        process.context = context
        self.process_manager.register(process)

        await self.event_manager.publish(
            event_type="process.created",
            source=process.id,
            payload={"type": process.type.value}
        )
        await self.start_process(process)
        return process
    
    async def start_process(self, process):
        self.process_manager.update_status(process.id, ProcessStatus.READY)
        self.scheduler.enqueue(process)
        await self.event_manager.publish(
            event_type="process.ready",
            source=process.id,
            payload={}
        )
        return process
    
    async def pause_process(self, process_id):
        process = self.process_manager.get(process_id)
        if not process: return
        self.process_manager.update_status(process_id, ProcessStatus.PAUSED)
        self.scheduler.pause(process_id)
        await self.event_manager.publish(event_type="process.paused", source=process_id, payload={})

    async def resume_process(self, process_id):
        """
        Handles the explicit OS-level state and scheduler queue transitions.
        Moves a process out of the WAITING queue back into the active READY queue.
        """
        process = self.process_manager.get(process_id)
        if not process: 
            return

        self.process_manager.update_status(process_id, ProcessStatus.READY)
        self.scheduler.wake(process_id)

        await self.event_manager.publish(
            event_type="process.resumed",
            source=process_id,
            payload={}
        )

    async def complete_process(self, process_id, result=None):
        self.process_manager.update_status(process_id, ProcessStatus.COMPLETED)
        await self.event_manager.publish(event_type="process.completed", source=process_id, payload={"result": result})

    async def fail_process(self, process_id, error):
        self.process_manager.update_status(process_id, ProcessStatus.FAILED)
        await self.event_manager.publish(event_type="process.failed", source=process_id, payload={"error": str(error)})

    async def terminate_process(self, process_id):
        self.process_manager.remove(process_id)
        await self.event_manager.publish(event_type="process.terminated", source=process_id, payload={})