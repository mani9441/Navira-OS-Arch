from runtime.process import (
    ProcessStatus
)


class SchedulerEventHandler:

    def __init__(
        self,
        scheduler,
        process_manager
    ):

        self.scheduler = (
            scheduler
        )

        self.process_manager = (
            process_manager
        )

    def on_human_requested(
        self,
        event
    ):

        process_id = (
            event.source
        )

        self.scheduler.wait(
            process_id
        )

        self.process_manager.update_status(
            process_id,
            ProcessStatus.WAITING
        )

    def on_human_responded(
        self,
        event
    ):

        process_id = (
            event.source
        )

        self.scheduler.wake(
            process_id
        )

        self.process_manager.update_status(
            process_id,
            ProcessStatus.READY
        )