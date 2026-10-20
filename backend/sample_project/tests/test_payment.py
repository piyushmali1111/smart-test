import pytest
from shop import payment
from sample_project.tests.helpers import simulate_io


def test_validate_card_valid():
    simulate_io(0.12)
    assert payment.validate_card("4111222233334444", 12, 2028, "123") is True


def test_validate_card_invalid_number():
    simulate_io(0.08)
    assert payment.validate_card("1234", 12, 2028, "123") is False


def test_validate_card_invalid_exp():
    simulate_io(0.08)
    assert payment.validate_card("4111222233334444", 13, 2028, "123") is False
    assert payment.validate_card("4111222233334444", 5, 2020, "123") is False


def test_validate_card_invalid_cvv():
    simulate_io(0.08)
    assert payment.validate_card("4111222233334444", 12, 2028, "AB") is False


def test_check_fraud_risk_normal():
    simulate_io(0.15)
    res = payment.check_fraud_risk("usr_101", 150.0)
    assert res["flagged"] is False
    assert res["risk_score"] < 0.50


def test_check_fraud_risk_high_amount():
    simulate_io(0.15)
    res = payment.check_fraud_risk("guest_999", 5500.0)
    assert res["flagged"] is True


def test_process_charge_success():
    simulate_io(0.30)
    card_data = {
        "number": "4111222233334444",
        "exp_month": 10,
        "exp_year": 2028,
        "cvv": "999",
    }
    res = payment.process_charge(100.0, "USD", card_data)
    assert res["success"] is True
    assert res["tx_id"].startswith("ch_")


def test_issue_refund_success_and_fail():
    simulate_io(0.20)
    res = payment.issue_refund("ch_1234567890abcdef", 50.0)
    assert res["success"] is True
    assert res["refund_id"].startswith("re_")

    fail_res = payment.issue_refund("bad_tx", 50.0)
    assert fail_res["success"] is False
