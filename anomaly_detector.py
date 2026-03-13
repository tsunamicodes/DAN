"""
anomaly_detector.py — AI-driven anomaly detection for DAN nodes.
Uses statistical profiling + Z-score analysis.
"""

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
    m = _mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))
def _zscore(val, v):
    m, s = _mean(v), _std(v)
    return (val - m) / s if s else 0.0


class AnomalyDetector:
    ZSCORE_THRESHOLD = 2.5
    FLOOD_RATE_THRESHOLD = 10
    MIN_SAMPLES = 5

    def __init__(self):
        self.profiles = {}
        self.total_anomalies = 0

    def _get_profile(self, node_id):
        if node_id not in self.profiles:
            self.profiles[node_id] = NodeProfile(node_id=node_id)
        return self.profiles[node_id]

    def update(self, snapshot):
        node_id = snapshot["node_id"]
        profile = self._get_profile(node_id)
        now = time.time()
        anomalies = []

        if not profile.last_snapshot:
            profile.last_snapshot = snapshot
            profile.last_update = now
            return anomalies

        elapsed = now - profile.last_update
        if elapsed < 0.1: return anomalies

        delta_sent = snapshot["messages_sent"] - profile.last_snapshot.get("messages_sent", 0)
        delta_broadcasts = snapshot["broadcast_count"] - profile.last_snapshot.get("broadcast_count", 0)
        delta_bytes = snapshot["bytes_sent"] - profile.last_snapshot.get("bytes_sent", 0)

        send_rate = delta_sent / elapsed
        broadcast_rate = delta_broadcasts / elapsed
        byte_rate = delta_bytes / elapsed

        profile.send_rates.append(send_rate)
        profile.broadcast_rates.append(broadcast_rate)
        profile.byte_rates.append(byte_rate)
        profile.last_snapshot = snapshot
        profile.last_update = now

        if len(profile.send_rates) < self.MIN_SAMPLES: return anomalies

        z_send = _zscore(send_rate, list(profile.send_rates)[:-1])
        if abs(z_send) > self.ZSCORE_THRESHOLD:
            anomalies.append({"node_id": node_id, "type": "SEND_RATE_SPIKE", "detail": f"Z-score={z_send:.2f}, rate={send_rate:.2f} msg/s", "severity": "HIGH" if z_send > 4.0 else "MEDIUM", "timestamp": now})

        if send_rate > self.FLOOD_RATE_THRESHOLD:
            anomalies.append({"node_id": node_id, "type": "FLOOD_ATTACK", "detail": f"Message rate={send_rate:.2f} msg/s exceeds threshold ({self.FLOOD_RATE_THRESHOLD})", "severity": "CRITICAL", "timestamp": now})

        z_broadcast = _zscore(broadcast_rate, list(profile.broadcast_rates)[:-1])
        if abs(z_broadcast) > self.ZSCORE_THRESHOLD:
            anomalies.append({"node_id": node_id, "type": "BROADCAST_ANOMALY", "detail": f"Z-score={z_broadcast:.2f}", "severity": "MEDIUM", "timestamp": now})

        avg_byte_rate = _mean(list(profile.byte_rates)[:-1])
        if avg_byte_rate > 0 and byte_rate > avg_byte_rate * 10:
            anomalies.append({"node_id": node_id, "type": "DATA_EXFIL_PATTERN", "detail": f"Byte rate={byte_rate:.0f} B/s is {byte_rate/avg_byte_rate:.1f}x above average", "severity": "HIGH", "timestamp": now})

        self.total_anomalies += len(anomalies)
        profile.anomaly_history.extend(anomalies)
        return anomalies

    def get_flagged_nodes(self):
        return [nid for nid, p in self.profiles.items() if p.anomaly_history]

    def summary(self):
        return {"total_anomalies": self.total_anomalies, "flagged_nodes": self.get_flagged_nodes()}
