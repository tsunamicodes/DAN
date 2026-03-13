"""
DAN — Decentralized Autonomous Network
Simulates a P2P mesh network.
"""
import argparse
import time
import threading
from network import DANetwork
from anomaly_detector import AnomalyDetector
from logger import NetworkLogger

def main():
    parser = argparse.ArgumentParser(description="DAN Simulator")
    parser.add_argument("--nodes", type=int, default=5, help="Number of nodes")
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--inject-anomaly", action="store_true")
    parser.add_argument("--log-file", default="logs/dan.log")
    args = parser.parse_args()
    print("=" * 55)
    print(f"  DAN | Nodes: {args.nodes} | Duration: {args.duration}s")
    print("=" * 55 + "\n")
    logger = NetworkLogger(args.log_file)
    detector = AnomalyDetector()
    network = DANetwork(node_count=args.nodes, logger=logger, detector=detector)
    network.start()
    if args.inject_anomaly:
        def inject():
            time.sleep(args.duration // 2)
            network.inject_rogue_node()
        threading.Thread(target=inject, daemon=True).start()
    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        pass
    finally:
        network.stop()
        report = network.summary()
        print(f"\nTotal messages: {report['total_messages']}")
        print(f"Anomalies: {report['anomalies_detected']}")
        logger.close()

if __name__ == "__main__":
    main()
