import pytest
from shop import order, user, payment, inventory, notification, report
from sample_project.tests.helpers import simulate_io


def test_e2e_complete_successful_checkout_flow():
    simulate_io(22.0)
    user_id = "usr_101"
    cart_obj = {"items": {"SKU-1001": 2, "SKU-1003": 5}}
    payment_info = {
        "number": "4111222233334444",
        "exp_month": 12,
        "exp_year": 2028,
        "cvv": "123",
    }
    shipping_address = {
        "region": "CA",
        "email": "alice@example.com",
    }

    ord_res = order.place_order(
        user_id=user_id,
        cart_obj=cart_obj,
        payment_info=payment_info,
        shipping_address=shipping_address,
        coupon_code="SAVE10",
        is_express=False,
    )

    assert ord_res["status"] == "confirmed"
    assert ord_res["user_id"] == user_id
    assert ord_res["totals"]["grand_total"] > 0
    assert ord_res["order_id"] in order.ORDER_REPOSITORY


def test_e2e_checkout_with_vip_discount():
    simulate_io(25.0)
    user_id = "usr_vip"
    cart_obj = {"items": {"SKU-1004": 2}}  # 240.00
    payment_info = {
        "number": "4111222233334444",
        "exp_month": 10,
        "exp_year": 2029,
        "cvv": "999",
    }
    shipping_address = {"region": "NY", "email": "diana@example.com"}

    ord_res = order.place_order(
        user_id=user_id,
        cart_obj=cart_obj,
        payment_info=payment_info,
        shipping_address=shipping_address,
        coupon_code="VIP50",
    )
    assert ord_res["totals"]["discount"] == 50.00
    assert ord_res["status"] == "confirmed"


def test_e2e_order_cancellation_flow():
    simulate_io(20.0)
    user_id = "usr_102"
    sku = "SKU-1005"
    cart_obj = {"items": {sku: 10}}
    initial_stock = inventory.INVENTORY_LEVELS[sku]

    payment_info = {
        "number": "4111222233334444",
        "exp_month": 11,
        "exp_year": 2027,
        "cvv": "456",
    }
    shipping_address = {"region": "TX", "email": "bob@example.com"}

    ord_res = order.place_order(
        user_id=user_id,
        cart_obj=cart_obj,
        payment_info=payment_info,
        shipping_address=shipping_address,
    )

    # Cancel order
    cancelled = order.cancel_order(ord_res["order_id"])
    assert cancelled["status"] == "cancelled"
    assert inventory.INVENTORY_LEVELS[sku] == initial_stock


def test_e2e_fraud_detection_rejection():
    simulate_io(16.0)
    cart_obj = {"items": {"SKU-1006": 30}}  # large order > 5000
    payment_info = {"number": "4111222233334444", "exp_month": 12, "exp_year": 2028, "cvv": "123"}
    shipping_address = {"region": "CA", "email": "fraud@example.com"}

    with pytest.raises(PermissionError):
        order.place_order(
            user_id="guest_suspicious",
            cart_obj=cart_obj,
            payment_info=payment_info,
            shipping_address=shipping_address,
        )


def test_e2e_empty_cart_error():
    simulate_io(15.0)
    with pytest.raises(ValueError):
        order.place_order(
            user_id="usr_101",
            cart_obj={"items": {}},
            payment_info={},
            shipping_address={},
        )


def test_e2e_insufficient_stock_rollback():
    simulate_io(18.0)
    cart_obj = {"items": {"SKU-1002": 20}}
    payment_info = {"number": "4111222233334444", "exp_month": 12, "exp_year": 2028, "cvv": "123"}
    shipping_address = {"region": "CA"}

    with pytest.raises(RuntimeError):
        order.place_order(
            user_id="usr_101",
            cart_obj=cart_obj,
            payment_info=payment_info,
            shipping_address=shipping_address,
        )


def test_e2e_invalid_payment_card_rejection():
    simulate_io(17.0)
    cart_obj = {"items": {"SKU-1001": 1}}
    payment_info = {"number": "bad_card", "exp_month": 12, "exp_year": 2028, "cvv": "123"}
    shipping_address = {"region": "CA"}

    with pytest.raises(RuntimeError):
        order.place_order(
            user_id="usr_101",
            cart_obj=cart_obj,
            payment_info=payment_info,
            shipping_address=shipping_address,
        )


def test_e2e_sales_report_aggregation():
    simulate_io(24.0)
    orders_list = list(order.ORDER_REPOSITORY.values())
    summary = report.generate_sales_summary(orders_list)
    assert summary["confirmed_orders"] >= 0
    assert summary["total_revenue"] >= 0.0


def test_e2e_profit_margin_reporting():
    simulate_io(26.0)
    orders_list = list(order.ORDER_REPOSITORY.values())
    margin = report.calculate_margin_report(orders_list)
    assert margin["margin_pct"] >= 0.0


def test_e2e_tax_ledger_reporting():
    simulate_io(23.0)
    orders_list = list(order.ORDER_REPOSITORY.values())
    tax_rep = report.export_tax_ledger(orders_list, region="CA")
    assert tax_rep["region"] == "CA"
    assert tax_rep["statutory_rate"] == 0.0825


def test_e2e_express_shipping_cost_impact():
    simulate_io(28.0)
    cart_obj = {"items": {"SKU-1001": 1}}
    p_info = {"number": "4111222233334444", "exp_month": 12, "exp_year": 2028, "cvv": "123"}
    ship_std = {"region": "CA", "email": "test@example.com"}

    o1 = order.place_order("usr_101", cart_obj, p_info, ship_std, is_express=False)
    o2 = order.place_order("usr_101", cart_obj, p_info, ship_std, is_express=True)
    assert o2["totals"]["shipping"] > o1["totals"]["shipping"]


def test_e2e_international_order_checkout():
    simulate_io(35.0)
    cart_obj = {"items": {"SKU-1002": 1}}
    p_info = {"number": "4111222233334444", "exp_month": 12, "exp_year": 2028, "cvv": "123"}
    ship_intl = {"region": "EU", "email": "eu_buyer@example.com"}

    o_intl = order.place_order("usr_101", cart_obj, p_info, ship_intl)
    assert o_intl["totals"]["tax"] > 0
    assert o_intl["status"] == "confirmed"
