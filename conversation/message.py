from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class Message:

    content: str

    user_id: str

    conversation_id: str

    id: str = str(uuid4())

    timestamp: str = datetime.utcnow().isoformat()