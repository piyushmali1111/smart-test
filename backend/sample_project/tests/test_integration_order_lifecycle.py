import pytest
from shop import order, validators, inventory, payment, notification
from sample_project.tests.helpers import simulate_io


def test_order_limits_validation_success():
    simulate_io(3.1)
    order_data = {
        "user_id": "usr_101",
        "items": [
            {"sku": "SKU-1001", "quantity": 10},
            {"sku": "SKU-1003", "quantity": 20},
        ],
    }
    assert order.check_limits(order_data) is True


def test_order_limits_validation_excess():
    simulate_io(3.0)
    order_data = {
        "user_id": "usr_101",
        "items": [{"sku": "SKU-1001", "quantity": 250}],
    }
    assert order.check_limits(order_data) is False


def test_circular_dependency_validators_and_order():
    simulate_io(4.2)
    order_data = {
        "items": [{"sku": "SKU-1001", "quantity": 5}],
    }
    # Direct call to validators.validate_order triggers order.check_limits
    assert validators.validate_order(order_data) is True
    # Direct call to order.check_limits triggers validators.validate_order
    assert order.check_limits(order_data) is True


def test_validate_and_reserve_success():
    simulate_io(3.5)
    items = {"SKU-1005": 5}
    assert order.validate_and_reserve(items) is True


def test_validate_and_reserve_insufficient():
    simulate_io(3.2)
    items = {"SKU-1006": 9999}
    assert order.validate_and_reserve(items) is False


def test_calculate_order_totals_standard():
    simulate_io(3.8)
    cart_obj = {"items": {"SKU-1001": 1}}
    totals = order.calculate_order_totals(cart_obj, region="CA", coupon_code="", is_express=False)
    assert totals["subtotal"] == 19.99
    assert totals["shipping"] > 0.0
    assert totals["grand_total"] > totals["subtotal"]


def test_calculate_order_totals_with_express_shipping():
    simulate_io(4.0)
    cart_obj = {"items": {"SKU-1001": 1}}
    std = order.calculate_order_totals(cart_obj, region="CA", coupon_code="", is_express=False)
    exp = order.calculate_order_totals(cart_obj, region="CA", coupon_code="", is_express=True)
    assert exp["shipping"] > std["shipping"]


def test_cancel_order_nonexistent():
    simulate_io(3.0)
    with pytest.raises(KeyError):
        order.cancel_order("ord_nonexistent_999")


def test_fraud_check_integration():
    simulate_io(3.3)
    risk_low = payment.check_fraud_risk("usr_101", 100.0)
    assert risk_low["flagged"] is False


def test_audit_logging_integration():
    simulate_io(3.2)
    notification.log_audit_event("INTEGRATION_CHECK", {"status": "ok"})
    assert any(log["event"] == "INTEGRATION_CHECK" for log in notification.NOTIFICATION_AUDIT_LOG)
