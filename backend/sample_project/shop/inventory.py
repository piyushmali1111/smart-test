"""Inventory tracking and stock reservation service."""

INVENTORY_LEVELS: dict[str, int] = {
    "SKU-1001": 250,
    "SKU-1002": 15,
    "SKU-1003": 500,
    "SKU-1004": 8,
    "SKU-1005": 1200,
    "SKU-1006": 4,
}

REORDER_THRESHOLDS: dict[str, int] = {
    "SKU-1001": 20,
    "SKU-1002": 10,
    "SKU-1003": 50,
    "SKU-1004": 5,
    "SKU-1005": 100,
    "SKU-1006": 3,
}


def check_stock(sku: str, requested_qty: int) -> bool:
    """Checks whether warehouse holds sufficient units for requested SKU."""
    if requested_qty <= 0:
        return False
    current = INVENTORY_LEVELS.get(sku, 0)
    return current >= requested_qty


def reserve_stock(sku: str, quantity: int) -> bool:
    """Attempts to deduct quantity from inventory stock."""
    if not check_stock(sku, quantity):
        return False
    INVENTORY_LEVELS[sku] -= quantity
    return True


def release_stock(sku: str, quantity: int) -> int:
    """Returns reserved quantity back into inventory."""
    if quantity <= 0:
        return INVENTORY_LEVELS.get(sku, 0)
    current = INVENTORY_LEVELS.get(sku, 0)
    INVENTORY_LEVELS[sku] = current + quantity
    return INVENTORY_LEVELS[sku]


def reorder_threshold_reached(sku: str) -> bool:
    """Determines whether stock level is below automated reorder threshold."""
    current = INVENTORY_LEVELS.get(sku, 0)
    threshold = REORDER_THRESHOLDS.get(sku, 10)
    return current <= threshold
