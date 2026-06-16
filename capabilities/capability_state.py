# capabilities/capability_state.py

from dataclasses import dataclass, field


@dataclass
class CapabilityState:

    query: str

    capability_name: str | None = None

    resolved_inputs: dict = field(
        default_factory=dict
    )

    missing_inputs: list[str] = field(
        default_factory=list
    )

    request_id: str | None = None

    checkpoint: str | None = None

    result: dict | None = None

    status: str = "running"