import json
from collections import defaultdict
from typing import List, Dict

DATA_PATH = "data/logs.json"


def _load_logs() -> List[Dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_logs() -> List[Dict]:
    return _load_logs()


def get_error_logs() -> List[Dict]:
    logs = _load_logs()
    return [log for log in logs if log["level"] in ("ERROR", "CRITICAL")]


def get_logs_by_level(level: str) -> List[Dict]:
    logs = _load_logs()
    level_up = level.upper()
    return [log for log in logs if log["level"] == level_up]


def get_logs_by_service(service_name: str) -> List[Dict]:
    logs = _load_logs()
    return [log for log in logs if log["service"] == service_name]


def list_services() -> List[str]:
    logs = _load_logs()
    services = sorted({log["service"] for log in logs})
    return services


def count_by_service(levels=("ERROR", "CRITICAL")) -> Dict[str, int]:
    logs = _load_logs()
    counts = defaultdict(int)
    for log in logs:
        if log["level"] in levels:
            counts[log["service"]] += 1
    return dict(counts)
