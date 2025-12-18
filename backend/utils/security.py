import re
import time
from typing import Dict, Tuple

try:
    from backend.utils.config import config
except ImportError:
    from utils.config import config


_RATE_LIMIT_BUCKET: Dict[str, Tuple[int, float]] = {}


def scrub_pii(text: str) -> str:
    """Remove common PII patterns before logging."""
    if not text:
        return ""
    scrubbed = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", "[email]", text)
    scrubbed = re.sub(r"\\b\\+?\\d[\\d\\s().-]{7,}\\b", "[phone]", scrubbed)
    return scrubbed


def check_api_key(provided_key: str) -> bool:
    """Simple static token check to gate external access."""
    if not config.API_AUTH_TOKEN:
        # No auth configured; allow by default for local/dev.
        return True
    return provided_key == config.API_AUTH_TOKEN


def is_rate_limited(client_id: str) -> bool:
    """
    Sliding window rate-limit. client_id can be IP or token.
    Returns True if limit exceeded.
    """
    if config.RATE_LIMIT_PER_MINUTE <= 0:
        return False

    now = time.time()
    window = 60
    bucket = _RATE_LIMIT_BUCKET.get(client_id, (0, now))
    count, start = bucket

    if now - start > window:
        _RATE_LIMIT_BUCKET[client_id] = (1, now)
        return False

    if count + 1 > config.RATE_LIMIT_PER_MINUTE:
        return True

    _RATE_LIMIT_BUCKET[client_id] = (count + 1, start)
    return False
