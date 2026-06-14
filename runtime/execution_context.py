from dataclasses import dataclass
from dataclasses import field


@dataclass
class ExecutionContext:

    query: str

    conversation_id: str

    user_id: str

    conversation_history: list = field(
        default_factory=list
    )

    process_context: dict = field(
        default_factory=dict
    )

    global_context: dict = field(
        default_factory=dict
    )

    active_processes: list = field(
        default_factory=list
    )