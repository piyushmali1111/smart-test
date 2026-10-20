"""User account and loyalty profile management."""

from shop import utils

USER_DATABASE: dict[str, dict] = {
    "usr_101": {"name": "Alice", "spend": 1250.0, "status": "active"},
    "usr_102": {"name": "Bob", "spend": 450.0, "status": "active"},
    "usr_103": {"name": "Charlie", "spend": 45.0, "status": "active"},
    "usr_vip": {"name": "Diana", "spend": 5500.0, "status": "vip"},
}


def get_user_profile(user_id: str) -> dict:
    """Retrieves user profile record from store."""
    if user_id.startswith("guest_"):
        return {
            "user_id": user_id,
            "name": "Guest Customer",
            "spend_total": 0.0,
            "status": "guest",
            "loyalty_tier": "bronze",
        }
    if user_id not in USER_DATABASE:
        raise KeyError(f"User {user_id} not found")
    record = USER_DATABASE[user_id]
    return {
        "user_id": user_id,
        "name": record["name"],
        "spend_total": record["spend"],
        "status": record["status"],
        "loyalty_tier": calculate_loyalty_tier(record["spend"]),
    }


def calculate_loyalty_tier(spend_total: float) -> str:
    """Calculates user loyalty level based on historical spending."""
    if spend_total >= 5000.0:
        return "platinum"
    if spend_total >= 1000.0:
        return "gold"
    if spend_total >= 250.0:
        return "silver"
    return "bronze"


def can_apply_vip_discount(user_id: str) -> bool:
    """Determines whether user is eligible for exclusive VIP promotions."""
    try:
        profile = get_user_profile(user_id)
        return profile["loyalty_tier"] in ("gold", "platinum")
    except KeyError:
        return False
