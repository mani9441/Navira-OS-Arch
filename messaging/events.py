from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class Event:

    event_type: str

    source: str

    payload: dict

    event_id: str = None

    timestamp: str = None

    def __post_init__(self):

        if self.event_id is None:

            self.event_id = str(
                uuid4()
            )

        if self.timestamp is None:

            self.timestamp = (
                datetime.utcnow()
                .isoformat()
            )