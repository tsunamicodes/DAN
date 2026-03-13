import uuid
import random
import time
import threading
from dataclasses import dataclass, field
from message import Message, MessageType

@dataclass
class NodeMetrics:
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    broadcast_count: int = 0
    avg_send_interval: float = 0.0
    _send_times: list = field(default_factory=list)

    def record_send(self):
        now = time.time()
        self._send_times.append(now)
        self.messages_sent += 1

class Node:
    def __init__(self, node_id=None, is_rogue=False):
        self.node_id = node_id or str(uuid.uuid4())[:8]
        self.is_rogue = is_rogue
        self.peers = []
        self.inbox = []
        self.metrics = NodeMetrics()
        self._lock = threading.Lock()
        self._running = False

    def connect_peer(self, peer):
        if peer not in self.peers and peer is not self:
            self.peers.append(peer)

    def receive(self, message):
        with self._lock:
            self.inbox.append(message)
            self.metrics.messages_received += 1

    def send(self, target, payload, msg_type=MessageType.DATA):
        msg = Message(sender_id=self.node_id, receiver_id=target.node_id, payload=payload, msg_type=msg_type)
        target.receive(msg)
        self.metrics.record_send()
        self.metrics.bytes_sent += len(payload.encode())
        return msg

    def broadcast(self, payload):
        for peer in self.peers:
            self.send(peer, payload, MessageType.BROADCAST)
        self.metrics.broadcast_count += 1

    def _normal_behavior(self):
        while self._running:
            time.sleep(random.uniform(1.5, 4.0))
            if self.peers:
                self.send(random.choice(self.peers), random.choice(["HEARTBEAT", f"DATA:{random.randint(1000,9999)}", f"SYNC:height={random.randint(100,500)}"]))

    def _rogue_behavior(self):
        while self._running:
            time.sleep(random.uniform(0.1, 0.3))
            if self.peers:
                self.broadcast(f"FLOOD:{uuid.uuid4().hex}")

    def start(self):
        self._running = True
        behavior = self._rogue_behavior if self.is_rogue else self._normal_behavior
        threading.Thread(target=behavior, daemon=True).start()

    def stop(self):
        self._running = False

    def snapshot(self):
        return {"node_id": self.node_id, "is_rogue": self.is_rogue, "peers": len(self.peers), "messages_sent": self.metrics.messages_sent, "messages_received": self.metrics.messages_received, "bytes_sent": self.metrics.bytes_sent, "broadcast_count": self.metrics.broadcast_count, "avg_send_interval": round(self.metrics.avg_send_interval, 3)}
