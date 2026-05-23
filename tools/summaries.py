from collections import Counter
from typing import Dict, List

from .logs import get_error_logs, get_all_logs


def summarize_errors() -> Dict:
    errors = get_error_logs()
    total = len(errors)
    services = sorted({e["service"] for e in errors})

    # Find most common issue by message text
    messages = [e["message"] for e in errors]
    most_common = None
    if messages:
        most_common = Counter(messages).most_common(1)[0][0]

    return {
        "total_errors": total,
        "services_affected": services,
        "most_common_issue": most_common,
    }


def recent_activity_summary(limit: int = 5) -> Dict:
    logs = get_all_logs()
    recent = logs[-limit:]
    levels = Counter([l["level"] for l in recent])
    services = sorted({l["service"] for l in recent})
    return {
        "recent_count": len(recent),
        "levels": dict(levels),
        "services": services,
    }
