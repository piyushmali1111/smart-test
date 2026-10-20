import pytest
from shop import inventory
from sample_project.tests.helpers import simulate_io


def test_check_stock_available():
    simulate_io(0.08)
    assert inventory.check_stock("SKU-1001", 10) is True


def test_check_stock_insufficient():
    simulate_io(0.08)
    assert inventory.check_stock("SKU-1006", 100) is False


def test_check_stock_zero_or_negative():
    simulate_io(0.05)
    assert inventory.check_stock("SKU-1001", 0) is False
    assert inventory.check_stock("SKU-1001", -2) is False


def test_reserve_stock_success_and_release():
    simulate_io(0.15)
    sku = "SKU-1003"
    initial = inventory.INVENTORY_LEVELS[sku]
    assert inventory.reserve_stock(sku, 5) is True
    assert inventory.INVENTORY_LEVELS[sku] == initial - 5
    inventory.release_stock(sku, 5)
    assert inventory.INVENTORY_LEVELS[sku] == initial


def test_reserve_stock_failure():
    simulate_io(0.10)
    assert inventory.reserve_stock("SKU-1004", 9999) is False


def test_release_stock_zero():
    simulate_io(0.05)
    sku = "SKU-1001"
    cur = inventory.INVENTORY_LEVELS[sku]
    assert inventory.release_stock(sku, 0) == cur


def test_reorder_threshold_not_reached():
    simulate_io(0.08)
    assert inventory.reorder_threshold_reached("SKU-1001") is False


def test_reorder_threshold_reached():
    simulate_io(0.08)
    # SKU-1004 has stock 8 and threshold 5; let's check SKU-1006 has stock 4, threshold 3
    # If we check a sku with 0 stock
    inventory.INVENTORY_LEVELS["SKU-TEMP"] = 2
    inventory.REORDER_THRESHOLDS["SKU-TEMP"] = 5
    assert inventory.reorder_threshold_reached("SKU-TEMP") is True
