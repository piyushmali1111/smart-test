import pytest
from shop import cart, pricing, discount, tax, shipping, inventory
from sample_project.tests.helpers import simulate_io


def test_cart_item_addition_and_subtotal_consistency():
    simulate_io(2.2)
    c = {}
    cart.add_item(c, "SKU-1001", 3)
    cart.add_item(c, "SKU-1003", 5)
    # 3 * 19.99 = 59.97, 5 * 8.00 = 40.00 -> 99.97
    assert cart.calculate_subtotal(c) == 99.97


def test_cart_removal_and_recalculation():
    simulate_io(2.5)
    c = {}
    cart.add_item(c, "SKU-1001", 2)
    cart.add_item(c, "SKU-1004", 1)
    cart.remove_item(c, "SKU-1001")
    assert cart.calculate_subtotal(c) == 120.00


def test_cart_checkout_with_tiered_discounts_and_tax():
    simulate_io(3.1)
    c = {}
    cart.add_item(c, "SKU-1003", 6)  # 6 items -> 48.00 subtotal, 8% bundle disc = 3.84
    res = cart.calculate_total(c, region="CA")
    assert res["subtotal"] == 48.00
    assert res["discount"] == 3.84
    assert res["total"] > 0.0


def test_cart_coupon_application_and_total():
    simulate_io(2.8)
    c = {}
    cart.add_item(c, "SKU-1004", 1)  # 120.00
    cart.apply_coupon(c, "SAVE20")  # 24.00 off -> 96.00
    res = cart.calculate_total(c, region="TX")
    assert res["discount"] == 24.00
    assert res["tax"] == 6.00  # 96.00 * 0.0625 = 6.00
    assert res["total"] == 102.00


def test_shipping_cost_estimation_for_multi_item_cart():
    simulate_io(2.4)
    items = [
        {"sku": "SKU-1001", "quantity": 2},
        {"sku": "SKU-1002", "quantity": 1},
    ]
    cost = shipping.calculate_shipping_cost(items, zone="domestic", is_express=False)
    assert cost == 8.99  # 0.90 + 1.20 = 2.10kg -> standard_medium: 8.99


def test_shipping_cost_express_air():
    simulate_io(2.6)
    items = [{"sku": "SKU-1001", "quantity": 1}]
    cost = shipping.calculate_shipping_cost(items, zone="domestic", is_express=True)
    assert cost == 24.99


def test_inventory_check_matches_cart_items():
    simulate_io(2.1)
    c = {"items": {"SKU-1001": 2, "SKU-1003": 10}}
    for sku, qty in c["items"].items():
        assert inventory.check_stock(sku, qty) is True


def test_cart_with_zero_tax_region_and_coupon():
    simulate_io(3.4)
    c = {"items": {"SKU-1004": 1}}
    cart.apply_coupon(c, "FLAT15")
    # subtotal 120, flat 15 off -> 105.00
    res = cart.calculate_total(c, region="DEFAULT")
    assert res["discount"] == 15.00
    assert res["total"] == 110.25  # 105 * 1.05 = 110.25


def test_cart_grand_total_incorporating_shipping():
    simulate_io(3.8)
    c = {"items": {"SKU-1003", 2}}
    c = {"items": {"SKU-1003": 2}}
    totals = cart.calculate_total(c, region="CA")
    items_list = [{"sku": "SKU-1003", "quantity": 2}]
    ship = shipping.calculate_shipping_cost(items_list, zone="domestic")
    grand = totals["total"] + ship
    assert grand > totals["total"]


def test_cart_item_update_edge_cases():
    simulate_io(2.5)
    c = {}
    cart.add_item(c, "SKU-1005", 10)
    assert cart.calculate_subtotal(c) == 52.50
    cart.add_item(c, "SKU-1005", 10)
    assert cart.calculate_subtotal(c) == 105.00
