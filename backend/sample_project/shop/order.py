"""Order processing, checkout workflow, and lifecycle management."""

from typing import Any
from shop import cart, payment, inventory, shipping, notification, user, utils

ORDER_REPOSITORY: dict[str, dict] = {}


def check_limits(order_data: dict[str, Any], depth: int = 0) -> bool:
    """Verifies that order items do not violate single-order quantities or velocity caps."""
    items = order_data.get("items", [])
    total_qty = sum(it.get("quantity", 0) for it in items)
    if total_qty > 200:
        return False

    # Circular dependency call back to validators
    from shop import validators
    if depth < 1:
        return validators.validate_order(order_data, depth=depth + 1)
    return True


def calculate_order_totals(
    cart_obj: dict[str, Any], region: str, coupon_code: str, is_express: bool = False
) -> dict[str, float]:
    """Calculates complete financial breakdown including freight shipping."""
    cart_breakdown = cart.calculate_total(cart_obj, region=region, coupon_code=coupon_code)

    items_list = [
        {"sku": sku, "quantity": qty}
        for sku, qty in cart_obj.get("items", {}).items()
    ]
    ship_cost = shipping.calculate_shipping_cost(items_list, zone="domestic", is_express=is_express)
    grand_total = utils.round_currency(cart_breakdown["total"] + ship_cost)

    return {
        "subtotal": cart_breakdown["subtotal"],
        "discount": cart_breakdown["discount"],
        "tax": cart_breakdown["tax"],
        "shipping": ship_cost,
        "grand_total": grand_total,
    }


def validate_and_reserve(items_dict: dict[str, int]) -> bool:
    """Checks inventory availability and reserves all line items."""
    for sku, qty in items_dict.items():
        if not inventory.check_stock(sku, qty):
            return False

    for sku, qty in items_dict.items():
        inventory.reserve_stock(sku, qty)
    return True


def place_order(
    user_id: str,
    cart_obj: dict[str, Any],
    payment_info: dict[str, Any],
    shipping_address: dict[str, Any],
    coupon_code: str = "",
    is_express: bool = False,
) -> dict[str, Any]:
    """High-level orchestration: reserves stock, processes charge, creates order, notifies."""
    items_dict = cart_obj.get("items", {})
    if not items_dict:
        raise ValueError("Cannot place order with empty cart")

    # 1. Check user profile
    profile = user.get_user_profile(user_id)

    # 2. Check limits and validate
    order_data = {
        "user_id": user_id,
        "items": [{"sku": s, "quantity": q} for s, q in items_dict.items()],
    }
    if not check_limits(order_data):
        raise ValueError("Order exceeds quantity limits")

    # 3. Calculate totals
    region = shipping_address.get("region", "CA")
    totals = calculate_order_totals(
        cart_obj, region=region, coupon_code=coupon_code, is_express=is_express
    )

    # 4. Check fraud
    fraud = payment.check_fraud_risk(user_id, totals["grand_total"])
    if fraud["flagged"]:
        raise PermissionError("Order flagged for fraud review")

    # 5. Reserve inventory
    if not validate_and_reserve(items_dict):
        raise RuntimeError("Insufficient stock to fulfill order")

    # 6. Process payment
    charge_res = payment.process_charge(totals["grand_total"], "USD", payment_info)
    if not charge_res["success"]:
        # Release reserved inventory
        for s, q in items_dict.items():
            inventory.release_stock(s, q)
        raise RuntimeError(f"Payment failed: {charge_res.get('error')}")

    # 7. Persist order
    gt = totals["grand_total"]
    tx = charge_res["tx_id"]
    order_id = f"ord_{utils.hash_string(f'{user_id}:{gt}:{tx}')[:10]}"
    order_record = {
        "order_id": order_id,
        "user_id": user_id,
        "customer_name": profile["name"],
        "items": items_dict,
        "totals": totals,
        "charge_id": charge_res["tx_id"],
        "status": "confirmed",
    }
    ORDER_REPOSITORY[order_id] = order_record

    # 8. Notify customer
    email_body = notification.format_order_email(
        order_id, totals["grand_total"], order_data["items"]
    )
    recipient = shipping_address.get("email", f"{user_id}@example.com")
    notification.send_email(recipient, f"Order Confirmation: {order_id}", email_body)
    notification.log_audit_event("ORDER_PLACED", {"order_id": order_id, "user_id": user_id})

    return order_record


def cancel_order(order_id: str) -> dict[str, Any]:
    """Cancels order, restores inventory, and triggers refund."""
    if order_id not in ORDER_REPOSITORY:
        raise KeyError(f"Order {order_id} not found")

    order_record = ORDER_REPOSITORY[order_id]
    if order_record["status"] == "cancelled":
        return order_record

    # Restore inventory
    for sku, qty in order_record.get("items", {}).items():
        inventory.release_stock(sku, qty)

    # Refund
    refund_res = payment.issue_refund(
        order_record["charge_id"], order_record["totals"]["grand_total"]
    )

    order_record["status"] = "cancelled"
    order_record["refund_id"] = refund_res.get("refund_id")
    notification.log_audit_event("ORDER_CANCELLED", {"order_id": order_id})
    return order_record
