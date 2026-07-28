"""
Per-model rate limiting and retry for the Gemini free tier.

Free tier ceilings are low and differ per model (5 requests per minute on
gemini-2.5-flash, higher on flash-lite, 100 on the embedding model), so the
limiter is keyed by model name rather than global. Without this the pipeline
runs fine on a handful of questions and falls over on the eval set.
"""

import time
from collections import defaultdict

from google.genai import errors as genai_errors

# Requests per minute to allow, per model. Set slightly under the published
# ceiling to leave room for clock skew.
LIMITS = {
    "gemini-2.5-flash": 4,
    "gemini-2.5-flash-lite": 12,
    "gemini-embedding-001": 90,
}
DEFAULT_LIMIT = 4

_history = defaultdict(list)


def throttle(model, n=1):
    """Block until n more requests fit inside the rolling minute for `model`."""
    limit = LIMITS.get(model, DEFAULT_LIMIT)
    while True:
        now = time.monotonic()
        hist = [t for t in _history[model] if now - t < 60]
        _history[model] = hist
        if len(hist) + n <= limit:
            _history[model].extend([now] * n)
            return
        time.sleep(max(0.5, 60 - (now - hist[0]) + 0.5))


def with_retry(fn, model, attempts=6):
    """Run fn(), retrying on quota errors with exponential backoff."""
    for attempt in range(attempts):
        try:
            throttle(model)
            return fn()
        except genai_errors.ClientError as e:
            msg = str(e)
            if "RESOURCE_EXHAUSTED" not in msg or attempt == attempts - 1:
                raise
            wait = min(70, 8 * (2 ** attempt))
            time.sleep(wait)
    raise RuntimeError("unreachable")
