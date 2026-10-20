import pytest
from shop import pricing
from sample_project.tests.helpers import simulate_io


def test_get_base_price_valid_items():
    simulate_io(0.10)
    assert pricing.get_base_price("SKU-1001") == 19.99
    assert pricing.get_base_price("SKU-1003") == 8.00


def test_get_base_price_invalid_item():
    simulate_io(0.08)
    with pytest.raises(KeyError):
        pricing.get_base_price("SKU-UNKNOWN")


def test_calculate_bulk_price_small_qty():
    simulate_io(0.12)
    # 5 * 8.00 = 40.00
    assert pricing.calculate_bulk_price("SKU-1003", 5) == 40.00


def test_calculate_bulk_price_tier_10():
    simulate_io(0.12)
    # 10 * (8.00 * 0.95 = 7.60) = 76.00
    assert pricing.calculate_bulk_price("SKU-1003", 10) == 76.00


def test_calculate_bulk_price_tier_20():
    simulate_io(0.12)
    # 20 * (8.00 * 0.90 = 7.20) = 144.00
    assert pricing.calculate_bulk_price("SKU-1003", 20) == 144.00


def test_calculate_bulk_price_tier_50():
    simulate_io(0.15)
    # 50 * (8.00 * 0.80 = 6.40) = 320.00
    assert pricing.calculate_bulk_price("SKU-1003", 50) == 320.00


def test_apply_markup_fraction():
    simulate_io(0.08)
    # cost 100, margin 0.25 -> 125.00
    assert pricing.apply_markup(100.0, 0.25) == 125.00


def test_apply_markup_percentage():
    simulate_io(0.08)
    # cost 50, margin 50 -> 75.00
    assert pricing.apply_markup(50.0, 50.0) == 75.00
