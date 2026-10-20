import pytest
from shop import cart
from sample_project.tests.helpers import simulate_io


def test_add_item_new():
    simulate_io(0.12)
    c = {}
    cart.add_item(c, "SKU-1001", 2)
    assert c["items"]["SKU-1001"] == 2


def test_add_item_existing():
    simulate_io(0.12)
    c = {"items": {"SKU-1001": 2}}
    cart.add_item(c, "SKU-1001", 3)
    assert c["items"]["SKU-1001"] == 5


def test_add_item_invalid_quantity():
    simulate_io(0.08)
    with pytest.raises(ValueError):
        cart.add_item({}, "SKU-1001", 0)


def test_remove_item():
    simulate_io(0.10)
    c = {"items": {"SKU-1001": 2, "SKU-1002": 1}}
    cart.remove_item(c, "SKU-1001")
    assert "SKU-1001" not in c["items"]
    assert "SKU-1002" in c["items"]


def test_apply_coupon_valid():
    simulate_io(0.15)
    c = {}
    cart.apply_coupon(c, "SAVE10")
    assert c["coupon"] == "SAVE10"


def test_apply_coupon_invalid():
    simulate_io(0.10)
    c = {}
    cart.apply_coupon(c, "NONEXISTENT")
    assert c["coupon"] is None


def test_calculate_subtotal():
    simulate_io(0.18)
    # SKU-1001: 19.99 * 2 = 39.98
    # SKU-1003: 8.00 * 1 = 8.00
    # total = 47.98
    c = {"items": {"SKU-1001": 2, "SKU-1003": 1}}
    assert cart.calculate_subtotal(c) == 47.98


def test_calculate_total_basic():
    simulate_io(0.25)
    # SKU-1003: 8.00 * 10 = 80.00
    # 10 items: bundle disc 15% -> 12.00
    # discounted: 68.00, CA tax (8.25%): 5.61
    # total: 73.61
    c = {"items": {"SKU-1003": 10}}
    res = cart.calculate_total(c, region="CA")
    assert res["subtotal"] == 80.00
    assert res["discount"] == 12.00
    assert res["tax"] == 5.61
    assert res["total"] == 73.61


def test_calculate_total_with_coupon():
    simulate_io(0.25)
    # SKU-1004: 120.00 * 1 = 120.00
    # SAVE20 coupon: 24.00 disc -> 96.00
    # NY tax (8.875%): 8.52 -> 104.52
    c = {"items": {"SKU-1004": 1}}
    res = cart.calculate_total(c, region="NY", coupon_code="SAVE20")
    assert res["subtotal"] == 120.00
    assert res["discount"] == 24.00
    assert res["tax"] == 8.52
    assert res["total"] == 104.52


def test_calculate_total_empty():
    simulate_io(0.10)
    res = cart.calculate_total({})
    assert res["subtotal"] == 0.0
    assert res["total"] == 0.0
