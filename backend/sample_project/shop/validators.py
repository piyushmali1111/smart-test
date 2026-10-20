"""Input and schema validators."""

import re
from typing import Any
from shop import utils


def validate_email(email: str) -> bool:
    """Validates basic email format."""
    if not email or "@" not in email:
        return False
    parts = email.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False
    domain_parts = parts[1].split(".")
    return (
        len(domain_parts) >= 2
        and bool(domain_parts[0])
        and len(domain_parts[-1]) >= 2
    )


def validate_sku(sku: str) -> bool:
    """Validates SKU alphanumeric format with hyphen prefix."""
    if not isinstance(sku, str) or len(sku) < 4:
        return False
    return bool(re.match(r"^[A-Z]{2,4}-[0-9]{3,6}$", sku))


def validate_quantity(qty: int) -> bool:
    """Validates that quantity is positive and within maximum limit."""
    return isinstance(qty, int) and 1 <= qty <= 999


def validate_order(order_data: dict[str, Any], depth: int = 0) -> bool:
    """Validates entire order data structure including limits verification."""
    if not isinstance(order_data, dict):
        return False
    items = order_data.get("items", [])
    if not items or len(items) > 50:
        return False

    for item in items:
        sku = item.get("sku", "")
        qty = item.get("quantity", 0)
        if not validate_sku(sku) or not validate_quantity(qty):
            return False

    # Circular dependency call to order.check_limits
    from shop import order
    if depth < 1:
        return order.check_limits(order_data, depth=depth + 1)
    return True
