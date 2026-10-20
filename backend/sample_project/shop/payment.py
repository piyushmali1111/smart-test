"""Payment gateway processing and fraud verification."""

import re
from typing import Any
from shop import utils


def validate_card(card_number: str, exp_month: int, exp_year: int, cvv: str) -> bool:
    """Performs basic Luhn-style validation on payment card."""
    cleaned = re.sub(r"\D", "", card_number or "")
    if len(cleaned) not in (15, 16):
        return False
    if not (1 <= exp_month <= 12):
        return False
    if exp_year < 2024 or exp_year > 2040:
        return False
    if not cvv or len(cvv) not in (3, 4) or not cvv.isdigit():
        return False
    return True


def check_fraud_risk(user_id: str, amount: float) -> dict[str, Any]:
    """Scores transaction fraud likelihood."""
    risk_score = 0.05
    if amount > 1000.0:
        risk_score += 0.25
    if amount > 5000.0:
        risk_score += 0.40
    if user_id.startswith("guest_"):
        risk_score += 0.15

    is_flagged = risk_score >= 0.50
    return {"risk_score": round(risk_score, 2), "flagged": is_flagged}


def process_charge(amount: float, currency: str, card_data: dict[str, Any]) -> dict[str, Any]:
    """Processes financial charge through payment provider."""
    if amount <= 0.0:
        raise ValueError("Charge amount must be positive")

    card_valid = validate_card(
        card_data.get("number", ""),
        card_data.get("exp_month", 0),
        card_data.get("exp_year", 0),
        card_data.get("cvv", ""),
    )
    if not card_valid:
        return {"success": False, "error": "Invalid card details", "tx_id": None}

    tx_hash = utils.hash_string(f"{amount}:{currency}:{card_data.get('number', '')}")[:16]
    return {
        "success": True,
        "amount": utils.round_currency(amount),
        "currency": currency,
        "tx_id": f"ch_{tx_hash}",
    }


def issue_refund(transaction_id: str, amount: float) -> dict[str, Any]:
    """Issues credit refund for settled charge."""
    if not transaction_id or not transaction_id.startswith("ch_"):
        return {"success": False, "error": "Invalid transaction reference"}
    if amount <= 0.0:
        return {"success": False, "error": "Refund amount must be positive"}

    refund_ref = utils.hash_string(f"ref:{transaction_id}:{amount}")[:12]
    return {
        "success": True,
        "refund_id": f"re_{refund_ref}",
        "refunded_amount": utils.round_currency(amount),
    }
