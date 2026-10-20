"""Shopping cart operations and order calculation."""

from typing import Any
from shop import pricing, discount, tax, utils


def add_item(cart: dict[str, Any], sku: str, quantity: int = 1) -> dict[str, Any]:
    """Adds item sku and quantity into cart dictionary."""
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    items = cart.setdefault("items", {})
    items[sku] = items.get(sku, 0) + quantity
    return cart


def remove_item(cart: dict[str, Any], sku: str) -> dict[str, Any]:
    """Removes an item completely from cart."""
    items = cart.get("items", {})
    if sku in items:
        del items[sku]
    return cart


def apply_coupon(cart: dict[str, Any], coupon_code: str) -> dict[str, Any]:
    """Attaches and validates voucher code on cart."""
    rule = discount.validate_coupon(coupon_code)
    if rule["valid"]:
        cart["coupon"] = coupon_code
    else:
        cart["coupon"] = None
    return cart


def calculate_subtotal(cart: dict[str, Any]) -> float:
    """Calculates sum of base prices across all items in cart."""
    items = cart.get("items", {})
    subtotal = 0.0
    for sku, qty in items.items():
        unit_price = pricing.get_base_price(sku)
        subtotal += unit_price * qty
    return utils.round_currency(subtotal)


def calculate_total(
    cart: dict[str, Any], region: str = "CA", coupon_code: str = ""
) -> dict[str, float]:
    """Computes final breakdown including subtotal, discounts, tax, and grand total."""
    subtotal = calculate_subtotal(cart)
    effective_coupon = coupon_code or cart.get("coupon") or ""

    total_items = sum(cart.get("items", {}).values())
    disc = discount.compute_final_discount(
        subtotal=subtotal, coupon_code=effective_coupon, item_count=total_items
    )

    discounted_subtotal = max(0.0, subtotal - disc)
    sales_tax = tax.calculate_sales_tax(discounted_subtotal, region)
    grand_total = utils.round_currency(discounted_subtotal + sales_tax)

    return {
        "subtotal": subtotal,
        "discount": disc,
        "tax": sales_tax,
        "total": grand_total,
    }
