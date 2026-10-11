"""
Brute-force protection for the login endpoint.

Tracks consecutive failed login attempts per account and temporarily locks
the account once the configured threshold is reached.
"""

import time
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class _LoginAttempts:
    failed: int = 0
    locked_until: float = 0.0


_attempts: dict[str, _LoginAttempts] = {}


def is_locked(email: str) -> bool:
    entry = _attempts.get(email)
    return entry is not None and entry.locked_until > time.time()


def register_failure(email: str) -> None:
    entry = _attempts.setdefault(email, _LoginAttempts())
    entry.failed += 1
    if entry.failed >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
        entry.locked_until = time.time() + settings.LOGIN_LOCKOUT_MINUTES * 60
        entry.failed = 0


def reset(email: str) -> None:
    _attempts.pop(email, None)
