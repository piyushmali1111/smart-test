"""Test simulation helpers."""

import os
import time

_CURRENT_SIMULATED_SECONDS: float = 0.0


def simulate_io(seconds: float) -> None:
    """Declare that this test would spend `seconds` on I/O.
    Does NOT sleep unless REAL_SLEEP=1.
    """
    global _CURRENT_SIMULATED_SECONDS
    _CURRENT_SIMULATED_SECONDS = max(_CURRENT_SIMULATED_SECONDS, float(seconds))
    if os.getenv("REAL_SLEEP", "0") == "1":
        time.sleep(seconds)


def get_and_reset_simulated_seconds() -> float:
    """Retrieves and resets simulated seconds for the active test."""
    global _CURRENT_SIMULATED_SECONDS
    val = _CURRENT_SIMULATED_SECONDS
    _CURRENT_SIMULATED_SECONDS = 0.0
    return val
