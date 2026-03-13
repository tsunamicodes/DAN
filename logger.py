"""
logger.py — Structured logging for DAN network events.
"""

import json
import os
from datetime import datetime


class NetworkLogger:
    def __init__(self, log_file):
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
        self._file = open(log_file, 'a')

    def log_snapshot(self, s): self._write({"event": "snapshot", "data": s})
    def log_anomaly(self, a): self._write({"event": "anomaly", "data": a})

    def _write(self, record):
        record["logged_at"] = datetime.now().isoformat()
        self._file.write(json.dumps(record) + "\n")
        self._file.flush()

    def close(self): self._file.close()
