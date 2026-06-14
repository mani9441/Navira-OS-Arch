from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class HumanRequest:
    request_id: str
    process_id: str
    question: str
    status: str
    response: Optional[str] = None
    created_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None