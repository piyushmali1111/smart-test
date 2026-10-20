"""Utility helpers for shop package."""

import hashlib
from typing import Any


def round_currency(amount: float) -> float:
    """Rounds an amount to 2 decimal places."""
    return round(float(amount) + 1e-9, 2)


def clamp(val: float, low: float, high: float) -> float:
    """Clamps a numeric value between low and high bounds."""
    if val < low:
        return low
    if val > high:
        return high
    return val


def hash_string(s: str) -> str:
    """Computes SHA-256 hash of a string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def format_currency(amount: float, currency: str = "USD") -> str:
    """Formats amount into formatted currency string."""
    rounded = round_currency(amount)
    if currency == "USD":
        return f"${rounded:.2f}"
    if currency == "EUR":
        return f"€{rounded:.2f}"
    return f"{rounded:.2f} {currency}"
