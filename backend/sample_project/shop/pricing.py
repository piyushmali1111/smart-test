"""Product pricing catalog and wholesale markup calculation."""

from shop import utils

CATALOG_PRICES: dict[str, float] = {
    "SKU-1001": 19.99,
    "SKU-1002": 49.50,
    "SKU-1003": 8.00,
    "SKU-1004": 120.00,
    "SKU-1005": 5.25,
    "SKU-1006": 250.00,
}


def get_base_price(sku: str) -> float:
    """Fetches unit catalog price for SKU item."""
    if sku not in CATALOG_PRICES:
        raise KeyError(f"Item SKU '{sku}' not recognized in pricing catalog")
    return CATALOG_PRICES[sku]


def calculate_bulk_price(sku: str, quantity: int) -> float:
    """Calculates tiered bulk purchase price with tiered quantity breaks."""
    base = get_base_price(sku)
    if quantity >= 50:
        unit_price = base * 0.80  # 20% volume discount
    elif quantity >= 20:
        unit_price = base * 0.90  # 10% volume discount
    elif quantity >= 10:
        unit_price = base * 0.95  # 5% volume discount
    else:
        unit_price = base
    total = unit_price * quantity
    return utils.round_currency(total)


def apply_markup(cost: float, margin_pct: float) -> float:
    """Calculates retail price from cost plus target gross margin percentage."""
    if cost < 0.0 or margin_pct < 0.0:
        raise ValueError("Cost and margin must be non-negative")
    if margin_pct >= 1.0:
        margin_pct = margin_pct / 100.0  # Allow 25 or 0.25 format
    retail = cost * (1.0 + margin_pct)
    return utils.round_currency(retail)
