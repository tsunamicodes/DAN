import json
import os
from datetime import datetime

class NetworkLogger:
    def __init__(self, log_file):
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
        self._file = open(log_file, 'a')

    def log_snapshot(self, snapshot):
        self._write({"event":"snapshot","data":snapshot})

    def log_anomaly(self, anomaly):
        self._write({"event":"anomaly","data":anomaly})

    def _write(self, record):
        record["logged_at"] = datetime.now().isoformat()
        self._file.write(json.dumps(record) + "\n")
        self._file.flush()

    def close(self):
        self._file.close()
