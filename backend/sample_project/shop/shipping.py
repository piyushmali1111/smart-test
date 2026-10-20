"""Shipping weight tiers and freight fee calculations."""

from shop import utils

ITEM_WEIGHTS: dict[str, float] = {
    "SKU-1001": 0.45,  # kg
    "SKU-1002": 1.20,
    "SKU-1003": 0.10,
    "SKU-1004": 4.50,
    "SKU-1005": 0.05,
    "SKU-1006": 8.00,
}


def calculate_shipping_weight(items: list[dict]) -> float:
    """Calculates cumulative package weight in kilograms."""
    total_weight = 0.0
    for item in items:
        sku = item.get("sku", "")
        qty = item.get("quantity", 1)
        unit_w = ITEM_WEIGHTS.get(sku, 0.50)
        total_weight += unit_w * qty
    return utils.round_currency(total_weight)


def get_shipping_tier(weight_kg: float, is_express: bool = False) -> str:
    """Classifies parcel weight tier."""
    if is_express:
        return "express_air"
    if weight_kg <= 1.0:
        return "standard_light"
    if weight_kg <= 5.0:
        return "standard_medium"
    return "freight_heavy"


def estimate_delivery_days(zone: str, is_express: bool = False) -> int:
    """Estimates transit business days based on zone and shipping speed."""
    base_days = {"domestic": 3, "regional": 5, "international": 10}.get(zone.lower(), 4)
    if is_express:
        return max(1, base_days // 2)
    return base_days


def calculate_shipping_cost(
    items: list[dict], zone: str = "domestic", is_express: bool = False
) -> float:
    """Calculates final shipping charge for items basket."""
    weight = calculate_shipping_weight(items)
    tier = get_shipping_tier(weight, is_express)

    base_rate = {
        "standard_light": 4.99,
        "standard_medium": 8.99,
        "freight_heavy": 18.50,
        "express_air": 24.99,
    }.get(tier, 9.99)

    zone_multiplier = {"domestic": 1.0, "regional": 1.35, "international": 2.2}.get(
        zone.lower(), 1.0
    )
    total_shipping = base_rate * zone_multiplier
    return utils.round_currency(total_shipping)
