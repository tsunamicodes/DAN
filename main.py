"""
DAN — Decentralized Autonomous Network
Simulates a P2P mesh network where each node communicates autonomously
and an AI-driven anomaly detector flags irregular behavior in real time.

Usage:
    python main.py --nodes 5 --duration 60
    python main.py --nodes 8 --inject-anomaly
"""

import argparse
import time
import threading
from network import DANetwork
from anomaly_detector import AnomalyDetector
from logger import NetworkLogger


def parse_args():
    parser = argparse.ArgumentParser(description="DAN — Decentralized Autonomous Network Simulator")
    parser.add_argument("--nodes", type=int, default=5, help="Number of nodes to simulate (default: 5)")
    parser.add_argument("--duration", type=int, default=60, help="Simulation duration in seconds (default: 60)")
    parser.add_argument("--inject-anomaly", action="store_true", help="Inject a rogue node mid-simulation")
    parser.add_argument("--log-file", type=str, default="logs/dan_network.log", help="Output log file path")
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 55)
    print("  DAN — Decentralized Autonomous Network Simulator")
    print("=" * 55)
    print(f"  Nodes: {args.nodes} | Duration: {args.duration}s | Anomaly injection: {args.inject_anomaly}")
    print("=" * 55 + "\n")

    logger = NetworkLogger(args.log_file)
    detector = AnomalyDetector()
    network = DANetwork(node_count=args.nodes, logger=logger, detector=detector)

    network.start()

    if args.inject_anomaly:
        def inject():
            time.sleep(args.duration // 2)
            print("\n[[!] Injecting rogue node into the network...")
            network.inject_rogue_node()
        threading.Thread(target=inject, daemon=True).start()

    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("\n[[!] Interrupted by user.")
    finally:
        network.stop()
        report = network.summary()
        print("\n" + "=" * 55)
        print("  SIMULATION SUMMARY")
        print("=" * 55)
        print(f"  Total messages sent       : {report['total_messages']}")
        print(f"  Anomalies detected        : {report['anomalies_detected']}")
        print(f"  Rogue nodes flagged       : {report['rogue_nodes_flagged']}")
        print(f"  Average message latency   : {report['avg_latency_ms']:.2f}ms")
        print(f"  Network uptime            : {report['uptime_seconds']}s")
        print(f"  Log saved to              : {args.log_file}")
        print("=" * 55)
        logger.close()


if __name__ == "__main__":
    main()
