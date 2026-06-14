from human.human_request import (
    HumanRequest
)


class ApprovalRequest(
    HumanRequest
):

    def __init__(
        self,
        process_id,
        title,
        message,
        metadata=None
    ):

        super().__init__(
            process_id=
                process_id,

            title=
                title,

            message=
                message,

            request_type=
                "approval",

            metadata=
                metadata
        )