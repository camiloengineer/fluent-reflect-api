import time
from typing import Dict, List
from fastapi import HTTPException

# In-memory storage for rate limiting
# In production, use Redis or similar
request_tracker: Dict[str, List[float]] = {}

def check_rate_limit(ip: str, limit: int = 20, window_seconds: int = 60) -> None:
    """
    Simple in-memory rate limiter.

    Args:
        ip: Client IP address
        limit: Maximum requests per window
        window_seconds: Time window in seconds

    Raises:
        HTTPException: If rate limit is exceeded
    """
    now = time.time()

    # Initialize tracker for new IPs
    if ip not in request_tracker:
        request_tracker[ip] = []

    # Clean old requests outside the time window
    request_tracker[ip] = [
        timestamp for timestamp in request_tracker[ip]
        if now - timestamp < window_seconds
    ]

    # Check if limit exceeded
    if len(request_tracker[ip]) >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {limit} requests per {window_seconds} seconds."
        )

    # Add current request
    request_tracker[ip].append(now)

def cleanup_old_ips(max_age_seconds: int = 3600) -> None:
    """
    Clean up old IP entries to prevent memory leaks.
    Call this periodically or on every N requests.
    """
    now = time.time()
    to_remove = []

    for ip, timestamps in request_tracker.items():
        # Remove IPs with no recent activity
        recent_requests = [t for t in timestamps if now - t < max_age_seconds]
        if not recent_requests:
            to_remove.append(ip)
        else:
            request_tracker[ip] = recent_requests

    for ip in to_remove:
        del request_tracker[ip]