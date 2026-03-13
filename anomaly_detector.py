import math
import time
from dataclasses import dataclass, field
from collections import deque

@dataclass
class NodeProfile:
    node_id: str
    send_rates: deque = field(default_factory=lambda: deque(maxlen=20))
    broadcast_rates: deque = field(default_factory=lambda: deque(maxlen=20))
    byte_rates: deque = field(default_factory=lambda: deque(maxlen=20))
    last_snapshot: dict = field(default_factory=dict)
    last_update: float = field(default_factory=time.time)
    anomaly_history: list = field(default_factory=list)

def _mean(v): return sum(v) / len(v) if v else 0.0
def _std(v):
    if len(v) < 2: return 0.0
    m = _mean(v); return math.sqrt(sum((x-m)**2 for x in v) / (len(v)-1))
def _zscore(val, vals):
    m = _mean(vals); s = _std(vals)
    return (val - m) / s if s else 0.0

class AnomalyDetector:
    ZSCORE_THRESHOLD = 2.5
    FLOOD_RATE_THRESHOLD = 10
    MIN_SAMPLES = 5

    def __init__(self):
        self.profiles = {}
        self.total_anomalies = 0

    def _update(self, nid):
        if nid not in self.profiles:
            self.profiles[nid] = NodeProfile(node_id=nid)
        return self.profiles[nid]

    def update(self, snapshot):
        nid = snapshot["node_id"]
        p = self._update(nid)
        now = time.time()
        anomalies = []
        if not p.last_snapshot:
            p.last_snapshot = snapshot; p.last_update = now; return anomalies
        elapsed = now - p.last_update
        if elapsed < 0.1: return anomalies
        ds = snapshot["messages_sent"] - p.last_snapshot.get("messages_sent", 0)
        db = snapshot["bytes_sent"] - p.last_snapshot.get("bytes_sent", 0)
        send_rate = ds / elapsed
        byte_rate = db / elapsed
        p.send_rates.append(send_rate); p.byte_rates.append(byte_rate)
        p.last_snapshot = snapshot; p.last_update = now
        if len(p.send_rates) < self.MIN_SAMPLES: return anomalies
        z = _zscore(send_rate, list(p.send_rates)[:-1])
        if abs(z) > self.ZSCORE_THRESHOLD:
            anomalies.append({"node_id": nid, "type": "SEND_RATE_SPIKE", "detail": f"Z-score={z:.2f}, rate={send_rate:.2f} msg/s", "severity": "HIGH" if z > 4.0 else "MEDIUM", "timestamp": now})
        if send_rate > self.FLOOD_RATE_THRESHOLD:
            anomalies.append({"node_id": nid, "type": "FLOOD_ATTACK", "detail": f"Message rate={send_rate:.2f} msg/s", "severity": "CRITICAL", "timestamp": now})
        self.total_anomalies += len(anomalies)
        p.anomaly_history.extend(anomalies)
        return anomalies

    def get_flagged_nodes(self):
        return [nid for nid, p in self.profiles.items() if p.anomaly_history]

