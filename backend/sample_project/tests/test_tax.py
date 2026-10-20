import pytest
from shop import tax
from sample_project.tests.helpers import simulate_io


def test_get_tax_rate_regions():
    simulate_io(0.08)
    assert tax.get_tax_rate("CA") == 0.0825
    assert tax.get_tax_rate("NY") == 0.08875
    assert tax.get_tax_rate("TX") == 0.0625
    assert tax.get_tax_rate("EU") == 0.20


def test_get_tax_rate_default_and_case():
    simulate_io(0.06)
    assert tax.get_tax_rate("unknown") == 0.05
    assert tax.get_tax_rate("ca") == 0.0825
    assert tax.get_tax_rate("") == 0.05


def test_calculate_sales_tax_ca():
    simulate_io(0.12)
    # 100 * 0.0825 = 8.25
    assert tax.calculate_sales_tax(100.0, "CA") == 8.25


def test_calculate_sales_tax_zero_or_negative():
    simulate_io(0.05)
    assert tax.calculate_sales_tax(0.0, "CA") == 0.0
    assert tax.calculate_sales_tax(-50.0, "CA") == 0.0


def test_calculate_sales_tax_eu():
    simulate_io(0.10)
    # 50.0 * 0.20 = 10.00
    assert tax.calculate_sales_tax(50.0, "EU") == 10.0


def test_calculate_sales_tax_fractional():
    simulate_io(0.12)
    # 33.33 * 0.0825 = 2.749725 -> 2.75
    assert tax.calculate_sales_tax(33.33, "CA") == 2.75


def test_apply_tax_exemptions_exempt():
    simulate_io(0.08)
    assert tax.apply_tax_exemptions(15.50, is_exempt=True) == 0.0


def test_apply_tax_exemptions_not_exempt():
    simulate_io(0.08)
    assert tax.apply_tax_exemptions(15.50, is_exempt=False) == 15.50
