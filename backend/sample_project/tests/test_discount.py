import pytest
from shop import discount
from sample_project.tests.helpers import simulate_io


def test_validate_coupon_valid_pct():
    simulate_io(0.12)
    res = discount.validate_coupon("SAVE10")
    assert res["valid"] is True
    assert res["type"] == "pct"
    assert res["value"] == 0.10


def test_validate_coupon_valid_flat():
    simulate_io(0.12)
    res = discount.validate_coupon("FLAT15")
    assert res["valid"] is True
    assert res["type"] == "flat"
    assert res["value"] == 15.0


def test_validate_coupon_invalid_or_empty():
    simulate_io(0.08)
    assert discount.validate_coupon("")["valid"] is False
    assert discount.validate_coupon("INVALID_CODE")["valid"] is False


def test_calculate_bundle_discount_tiers():
    simulate_io(0.15)
    # >= 10 items: 15%
    assert discount.calculate_bundle_discount(10, 100.0) == 15.0
    # >= 5 items: 8%
    assert discount.calculate_bundle_discount(6, 100.0) == 8.0
    # >= 3 items: 3%
    assert discount.calculate_bundle_discount(3, 100.0) == 3.0
    # < 3 items: 0%
    assert discount.calculate_bundle_discount(2, 100.0) == 0.0


def test_apply_seasonal_discount_holiday():
    simulate_io(0.10)
    assert discount.apply_seasonal_discount(200.0, month=12) == 10.0
    assert discount.apply_seasonal_discount(50.0, month=12) == 0.0  # below 100


def test_apply_seasonal_discount_summer():
    simulate_io(0.10)
    assert discount.apply_seasonal_discount(100.0, month=7) == 3.0
    assert discount.apply_seasonal_discount(50.0, month=7) == 0.0  # below 80


def test_apply_seasonal_discount_other_months():
    simulate_io(0.08)
    assert discount.apply_seasonal_discount(200.0, month=5) == 0.0


def test_compute_final_discount_with_coupon():
    simulate_io(0.20)
    # subtotal 100, SAVE20 (min spend 50) -> 20.0
    res = discount.compute_final_discount(100.0, coupon_code="SAVE20", item_count=1)
    assert res == 20.0


def test_compute_final_discount_coupon_min_spend_not_met():
    simulate_io(0.15)
    # subtotal 30, SAVE20 min spend is 50 -> 0.0
    res = discount.compute_final_discount(30.0, coupon_code="SAVE20", item_count=1)
    assert res == 0.0


def test_compute_final_discount_clamped_to_70_pct():
    simulate_io(0.25)
    # subtotal 100, flat 50 + 10 items (15%) + holiday (5%) = 70%
    res = discount.compute_final_discount(100.0, coupon_code="VIP50", item_count=12, month=12)
    # VIP50 requires min spend 150, so VIP50 is not active; bundle=15, seasonal=5 -> 20
    assert res == 20.0
