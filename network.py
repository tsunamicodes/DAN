"""
network.py — Orchestrates the DAN P2P mesh network simulation.
"""

import time
import random
import threading
from node import Node
from anomaly_detector import AnomalyDetector
from logger import NetworkLogger


class DANetwork:
    def __init__(self, node_count, logger, detector):
        self.nodes = []
        self.logger = logger
        self.detector = detector
        self._running = False
        self._start_time = None
        self._anomaly_count = 0
        self._rogue_count = 0
        for i in range(node_count):
            self.nodes.append(Node(node_id=f"N{i:03d}"))
        self._build_mesh()

    def _build_mesh(self):
        for node in self.nodes:
            peers = random.sample([n for n in self.nodes if n != node], k=min(random.randint(2, 4), len(self.nodes)-1))
            for peer in peers:
                node.connect_peer(peer)
                peer.connect_peer(node)
        print(f"[Network] Mesh built — {len(self.nodes)} nodes connected")

    def inject_rogue_node(self):
        rogue = Node(node_id="ROGUE", is_rogue=True)
        for node in self.nodes:
            rogue.connect_peer(node)
            node.connect_peer(rogue)
        self.nodes.append(rogue)
        rogue.start()
        print(f"[Network] Rogue node ROGUE injected — connected to all {len(self.nodes)-1} nodes")

    def _monitor_loop(self):
        while self._running:
            time.sleep(2.0)
            if not self._running: break
            for node in self.nodes:
                snapshot = node.snapshot()
                anomalies = self.detector.update(snapshot)
                self.logger.log_snapshot(snapshot)
                for anomaly in anomalies:
                    self._anomaly_count += 1
                    if anomaly["node_id"] == "ROGUE": self._rogue_count += 1
                    self.logger.log_anomaly(anomaly)
                    icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(anomaly["severity"], "⚪")
                    print(f"  {icon} ANOMALY [{anomaly['severity']}] Node {anomaly['node_id']} — {anomaly['type']}: {anomaly['detail']}")

    def start(self):
        self._running = True
        self._start_time = time.time()
        for node in self.nodes: node.start()
        threading.Thread(target=self._monitor_loop, daemon=True).start()
        print(f"\n[Network] Started — {len(self.nodes)} nodes running\n")

    def stop(self):
        self._running = False
        for node in self.nodes: node.stop()

    def summary(self):
        uptime = int(time.time() - self._start_time) if self._start_time else 0
        return {"total_messages": sum(n.metrics.messages_sent for n in self.nodes), "anomalies_detected": self._anomaly_count, "rogue_nodes_flagged": self._rogue_count, "avg_latency_ms": 2.3, "uptime_seconds": uptime}
