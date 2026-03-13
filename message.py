"""
message.py — Message protocol for DAN nodes.
"""

import uuid
import time
from dataclasses import dataclass, field
from enum import Enum


class MessageType(Enum):
    DATA = "DATA"
    HEARTBEAT = "HEARTBEAT"
    BROADCAST = "BROADCAST"
    SYNC = "SYNC"
    ALERT = "ALERT"


@dataclass
class Message:
    sender_id: str
    receiver_id: str
    payload: str
    msg_type: MessageType = MessageType.DATA
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {"message_id": self.message_id, "sender_id": self.sender_id, "receiver_id": self.receiver_id, "payload": self.payload, "msg_type": self.msg_type.value, "timestamp": self.timestamp}
