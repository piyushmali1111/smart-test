"""Discounts, coupon vouchers, and seasonal promotions."""

from shop import utils

COUPONS: dict[str, dict] = {
    "SAVE10": {"type": "pct", "value": 0.10, "min_spend": 20.0},
    "SAVE20": {"type": "pct", "value": 0.20, "min_spend": 50.0},
    "FLAT15": {"type": "flat", "value": 15.0, "min_spend": 60.0},
    "VIP50": {"type": "flat", "value": 50.0, "min_spend": 150.0},
}


def validate_coupon(code: str) -> dict:
    """Validates coupon voucher code and returns rule specification."""
    if not code:
        return {"valid": False, "discount": 0.0, "type": "none"}
    normalized = code.strip().upper()
    if normalized in COUPONS:
        rule = COUPONS[normalized]
        return {
            "valid": True,
            "code": normalized,
            "type": rule["type"],
            "value": rule["value"],
            "min_spend": rule["min_spend"],
        }
    return {"valid": False, "discount": 0.0, "type": "none"}


def calculate_bundle_discount(item_count: int, subtotal: float) -> float:
    """Computes tiered volume discount based on total items in basket."""
    if item_count >= 10:
        return utils.round_currency(subtotal * 0.15)
    if item_count >= 5:
        return utils.round_currency(subtotal * 0.08)
    if item_count >= 3:
        return utils.round_currency(subtotal * 0.03)
    return 0.0


def apply_seasonal_discount(subtotal: float, month: int) -> float:
    """Computes seasonal promotion discount based on calendar month."""
    # Month 11/12: Holiday sale (5% off)
    if month in (11, 12) and subtotal >= 100.0:
        return utils.round_currency(subtotal * 0.05)
    # Month 7: Summer sale (3% off)
    if month == 7 and subtotal >= 80.0:
        return utils.round_currency(subtotal * 0.03)
    return 0.0


def compute_final_discount(
    subtotal: float, coupon_code: str = "", item_count: int = 1, month: int = 6
) -> float:
    """Combines coupon, bundle, and seasonal discounts safely without exceeding subtotal."""
    if subtotal <= 0.0:
        return 0.0

    total_discount = 0.0
    rule = validate_coupon(coupon_code)
    if rule["valid"] and subtotal >= rule.get("min_spend", 0.0):
        if rule["type"] == "pct":
            total_discount += subtotal * rule["value"]
        elif rule["type"] == "flat":
            total_discount += rule["value"]

    bundle_disc = calculate_bundle_discount(item_count, subtotal)
    seasonal_disc = apply_seasonal_discount(subtotal, month)

    total_discount += bundle_disc + seasonal_disc
    max_allowed = subtotal * 0.70  # Maximum discount cap is 70% of subtotal
    clamped = utils.clamp(total_discount, 0.0, max_allowed)
    return utils.round_currency(clamped)
