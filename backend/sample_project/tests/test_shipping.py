import pytest
from shop import shipping
from sample_project.tests.helpers import simulate_io


def test_calculate_shipping_weight_single():
    simulate_io(0.12)
    items = [{"sku": "SKU-1001", "quantity": 2}]
    # 0.45 * 2 = 0.90
    assert shipping.calculate_shipping_weight(items) == 0.90


def test_calculate_shipping_weight_multiple():
    simulate_io(0.15)
    items = [
        {"sku": "SKU-1001", "quantity": 1},  # 0.45
        {"sku": "SKU-1002", "quantity": 1},  # 1.20
        {"sku": "SKU-1003", "quantity": 3},  # 0.10 * 3 = 0.30
    ]
    assert shipping.calculate_shipping_weight(items) == 1.95


def test_get_shipping_tier_express():
    simulate_io(0.06)
    assert shipping.get_shipping_tier(0.5, is_express=True) == "express_air"


def test_get_shipping_tier_by_weight():
    simulate_io(0.08)
    assert shipping.get_shipping_tier(0.8) == "standard_light"
    assert shipping.get_shipping_tier(3.0) == "standard_medium"
    assert shipping.get_shipping_tier(8.5) == "freight_heavy"


def test_estimate_delivery_days_standard():
    simulate_io(0.08)
    assert shipping.estimate_delivery_days("domestic") == 3
    assert shipping.estimate_delivery_days("regional") == 5
    assert shipping.estimate_delivery_days("international") == 10


def test_estimate_delivery_days_express():
    simulate_io(0.08)
    assert shipping.estimate_delivery_days("domestic", is_express=True) == 1
    assert shipping.estimate_delivery_days("international", is_express=True) == 5


def test_calculate_shipping_cost_domestic_light():
    simulate_io(0.18)
    items = [{"sku": "SKU-1003", "quantity": 2}]  # 0.2 kg -> standard_light: 4.99
    assert shipping.calculate_shipping_cost(items, "domestic") == 4.99


def test_calculate_shipping_cost_international():
    simulate_io(0.20)
    items = [{"sku": "SKU-1003", "quantity": 2}]  # standard_light: 4.99 * 2.2 = 10.978 -> 10.98
    assert shipping.calculate_shipping_cost(items, "international") == 10.98
