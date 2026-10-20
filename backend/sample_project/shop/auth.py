"""Authentication and authorization utilities."""

from shop import utils

SALT = "smarttest-salt-2026"


def hash_password(raw_password: str) -> str:
    """Hashes password with SHA256 and internal salt."""
    if len(raw_password) < 6:
        raise ValueError("Password too short")
    return utils.hash_string(f"{raw_password}:{SALT}")


def verify_token(token: str) -> dict[str, str]:
    """Decodes and verifies authentication bearer token."""
    if not token or not token.startswith("tok_"):
        raise PermissionError("Invalid token format")
    payload = token[4:]
    if len(payload) < 8:
        raise PermissionError("Malformed token")
    parts = payload.split("_", 1)
    user_id = parts[0]
    role = parts[1] if len(parts) > 1 else "user"
    return {"user_id": user_id, "role": role}


def check_permission(role: str, action: str) -> bool:
    """Checks role-based access control permissions."""
    admin_actions = {"refund", "export_tax", "reorder_stock", "cancel_any_order"}
    manager_actions = {"reorder_stock", "export_tax"}

    if role == "admin":
        return True
    if role == "manager" and action in manager_actions:
        return True
    if role == "user" and action not in admin_actions and action not in manager_actions:
        return True
    return False
