from human.human_request import (
    HumanRequest
)

from human.approval_request import (
    ApprovalRequest
)


class HumanRuntime:

    def __init__(
        self,
        human_queue,
        scheduler,
        process_manager
    ):

        self.human_queue = (
            human_queue
        )

        self.scheduler = (
            scheduler
        )

        self.process_manager = (
            process_manager
        )

    def request_input(
        self,
        process_id,
        title,
        message,
        metadata=None
    ):

        request = HumanRequest(
            process_id=
                process_id,

            title=
                title,

            message=
                message,

            metadata=
                metadata
        )

        self.human_queue.add(
            request
        )

        return request

    def request_approval(
        self,
        process_id,
        title,
        message,
        metadata=None
    ):

        request = ApprovalRequest(
            process_id=
                process_id,

            title=
                title,

            message=
                message,

            metadata=
                metadata
        )

        self.human_queue.add(
            request
        )

        return request