# DAN — Decentralized Autonomous Network 🌐

A Python simulation of a **peer-to-peer mesh network** with an AI-driven anomaly detection engine. DAN models how decentralized nodes communicate autonomously, and how behavioral analysis can identify rogue or compromised nodes in real time.

---

## Overview

DAN creates a network of independent nodes that:
- Self-organize into a partial mesh topology
- Communicate via a custom message protocol (heartbeats, data blocks, sync messages)
- Are monitored continuously by a statistical anomaly detector

A rogue node can be injected mid-simulation to trigger flood detection — demonstrating the system's detection capabilities in a live scenario.

---

## Architecture

```
main.py                 ← CLI entry point & simulation runner
├── network.py           ← Orchestrates the mesh, starts monitor loop
├── node.py             ← Individual P2P node (normal or fogue behavior)
├── message.py           ← Message dataclass + MessageType enum
├── anomaly_detector.py  ← Statistical anomaly detection engine
└── logger.py            ← Structured JSON event logger
```

### Network Topology

Nodes are connected in a randomized **partial mesh**: each node connects bidirectionally to 2–4 random peers. This simulates real P2P networks (Gossip protocols, DHT overlays).

---

## Anomaly Detection Engine

The `AnomalyDetector` builds a **rolling behavioral profile** for each node and uses statistical analysis to flag deviations:

| Detection Rule | Method | Severity |
|---|---|---|
| Send rate spike | Z-score | MEDIUM / HIGH |
| Flood attack | Absolute rate > 10 msg/s | CRITICAL |
| Broadcast anomaly | Z-score on broadcast frequency | MEDIUM |
| Data exfiltration pattern | Byte rate > 10x rolling average | HIGH |

Uses Z-score normalization over a rolling window of 20 samples - no external ML libraries required.

---

## Setup & Usage

```bash
git clone https://github.com/tsunamicodes/dan.git
cd dan

# Python 3.10+ required, no pip installs needed

# Basic simulation (5 nodes, 60 seconds)
python main.py

# Custom config
python main.py --nodes 8 --duration 90

# Inject a rogue node halfway through
python main.py --nodes 6 --duration 60 --inject-anomaly
```

---

## Tech Stack

- Python 3.10+ (standard library only)
- threading - concurrent node simulation
- dataclasses - structured message/profile modeling
- collections.deque - efficient rolling window statistics
- Custom Z-score engine - no sklearn dependency

---

## Author

**Suhani Rastogi** - B.Tech CSE (Cybersecurity), Bennett University
CEH v13 Certified
