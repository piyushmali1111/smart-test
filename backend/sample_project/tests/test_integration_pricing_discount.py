import pytest
from shop import pricing, discount, user, utils
from sample_project.tests.helpers import simulate_io


def test_wholesale_pricing_bulk_break_computation():
    simulate_io(2.3)
    p = pricing.calculate_bulk_price("SKU-1003", 50)
    assert p == 320.00


def test_markup_plus_tiered_discount():
    simulate_io(2.7)
    base_cost = 50.0
    retail_price = pricing.apply_markup(base_cost, 0.40)  # 70.00
    disc = discount.calculate_bundle_discount(5, retail_price)  # 8% of 70.00 = 5.60
    assert disc == 5.60


def test_vip_user_discount_qualification():
    simulate_io(3.0)
    is_vip = user.can_apply_vip_discount("usr_vip")
    assert is_vip is True
    disc = discount.compute_final_discount(200.0, coupon_code="VIP50")
    assert disc == 50.00


def test_normal_user_vip_coupon_rejection():
    simulate_io(2.5)
    # normal user spend 45.0
    is_vip = user.can_apply_vip_discount("usr_103")
    assert is_vip is False


def test_multiple_sku_bulk_pricing():
    simulate_io(3.2)
    p1 = pricing.calculate_bulk_price("SKU-1001", 20)  # 19.99 * 0.90 * 20 = 359.82
    p2 = pricing.calculate_bulk_price("SKU-1002", 10)  # 49.50 * 0.95 * 10 = 470.25
    assert p1 > 0 and p2 > 0


def test_discount_does_not_exceed_cap():
    simulate_io(3.5)
    # subtotal 100, maximum discount allowed is 70% (70.00)
    disc = discount.compute_final_discount(100.0, coupon_code="VIP50", item_count=20, month=12)
    assert disc <= 70.00


def test_pricing_and_currency_formatting():
    simulate_io(2.2)
    price = pricing.get_base_price("SKU-1004")
    assert utils.format_currency(price, "USD") == "$120.00"


def test_holiday_sale_pricing_flow():
    simulate_io(2.9)
    subtotal = 300.0
    disc = discount.compute_final_discount(subtotal, coupon_code="SAVE10", month=12)
    # SAVE10: 30.00 + holiday: 15.00 = 45.00
    assert disc == 45.00


def test_discount_on_zero_subtotal():
    simulate_io(2.0)
    assert discount.compute_final_discount(0.0, coupon_code="SAVE20") == 0.0


def test_invalid_coupon_fallback():
    simulate_io(2.4)
    disc = discount.compute_final_discount(150.0, coupon_code="GARBAGE_CODE", item_count=5)
    # bundle discount 8% of 150 = 12.00
    assert disc == 12.00
