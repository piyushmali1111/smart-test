import pytest
from shop import validators
from sample_project.tests.helpers import simulate_io


def test_validate_email_valid():
    simulate_io(0.12)
    assert validators.validate_email("alice@example.com") is True
    assert validators.validate_email("user.name+tag@sub.domain.co") is True


def test_validate_email_invalid():
    simulate_io(0.08)
    assert validators.validate_email("") is False
    assert validators.validate_email("invalid-email") is False
    assert validators.validate_email("@missinguser.com") is False
    assert validators.validate_email("user@.com") is False


def test_validate_sku_valid():
    simulate_io(0.10)
    assert validators.validate_sku("SKU-1001") is True
    assert validators.validate_sku("AB-12345") is True


def test_validate_sku_invalid():
    simulate_io(0.06)
    assert validators.validate_sku("") is False
    assert validators.validate_sku("12345") is False
    assert validators.validate_sku("sku_1001") is False


def test_validate_quantity_valid():
    simulate_io(0.05)
    assert validators.validate_quantity(1) is True
    assert validators.validate_quantity(50) is True
    assert validators.validate_quantity(999) is True


def test_validate_quantity_invalid():
    simulate_io(0.05)
    assert validators.validate_quantity(0) is False
    assert validators.validate_quantity(-5) is False
    assert validators.validate_quantity(1000) is False


def test_validate_order_valid_structure():
    simulate_io(0.25)
    order_data = {
        "items": [
            {"sku": "SKU-1001", "quantity": 2},
            {"sku": "SKU-1002", "quantity": 1},
        ]
    }
    assert validators.validate_order(order_data) is True


def test_validate_order_empty_or_invalid():
    simulate_io(0.15)
    assert validators.validate_order({}) is False
    assert validators.validate_order({"items": []}) is False
    assert validators.validate_order({"items": [{"sku": "BAD", "quantity": 1}]}) is False
