"""Customer communication and logging."""

from typing import Any
from shop import utils

NOTIFICATION_AUDIT_LOG: list[dict[str, Any]] = []


def format_order_email(order_id: str, total: float, items: list[dict]) -> str:
    """Builds confirmation email template text."""
    currency_str = utils.format_currency(total)
    item_lines = [
        f"- {it.get('sku')}: {it.get('quantity')}x" for it in items
    ]
    items_block = "\n".join(item_lines)
    return (
        f"Thank you for your order {order_id}!\n"
        f"Total: {currency_str}\n"
        f"Items:\n{items_block}\n"
        "Your order will be dispatched shortly."
    )


def send_email(recipient: str, subject: str, body: str) -> bool:
    """Dispatches transactional email to customer."""
    if not recipient or "@" not in recipient:
        return False
    log_audit_event("EMAIL_SENT", {"recipient": recipient, "subject": subject})
    return True


def send_sms(phone: str, message: str) -> bool:
    """Dispatches SMS text alert."""
    if not phone or len(phone) < 8:
        return False
    log_audit_event("SMS_SENT", {"phone": phone, "length": len(message)})
    return True


def log_audit_event(event_type: str, details: dict[str, Any]) -> None:
    """Appends record to internal audit ledger."""
    NOTIFICATION_AUDIT_LOG.append({
        "event": event_type,
        "details": details,
    })
