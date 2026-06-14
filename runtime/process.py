from enum import Enum
from uuid import uuid4
from datetime import datetime


class ProcessType(Enum):

    CAPABILITY = "capability"

    WORKFLOW = "workflow"

    TEAM = "team"

    PLANNER = "planner"

    CONVERSATION = "conversation"


class ProcessStatus(Enum):

    CREATED = "created"

    READY = "ready"

    RUNNING = "running"

    PAUSED = "paused"

    WAITING = "waiting"

    COMPLETED = "completed"

    FAILED = "failed"

    TERMINATED = "terminated"


class Process:

    def __init__(
        self,
        process_type,
        owner=None,
        metadata=None,
        context=None
    ):

        self.id = str(uuid4())

        self.type = process_type

        self.status = (
            ProcessStatus.CREATED
        )

        self.owner = owner

        self.metadata = (
            metadata or {}
        )

        self.context = context

        self.created_at = (
            datetime.utcnow()
        )

        self.updated_at = (
            datetime.utcnow()
        )

    def set_status(
        self,
        status
    ):

        self.status = status

        self.updated_at = (
            datetime.utcnow()
        )

    def is_active(self):

        return self.status in [

            ProcessStatus.READY,

            ProcessStatus.RUNNING,

            ProcessStatus.WAITING,

            ProcessStatus.PAUSED
        ]

    def is_finished(self):

        return self.status in [

            ProcessStatus.COMPLETED,

            ProcessStatus.FAILED,

            ProcessStatus.TERMINATED
        ]

    def to_dict(self):

        return {

            "id":
                self.id,

            "type":
                self.type.value,

            "status":
                self.status.value,

            "owner":
                self.owner,

            "metadata":
                self.metadata,

            "created_at":
                self.created_at.isoformat(),

            "updated_at":
                self.updated_at.isoformat()
        }

    def __repr__(self):

        return (
            f"Process("
            f"id={self.id}, "
            f"type={self.type.value}, "
            f"status={self.status.value}"
            f")"
        )
    

    