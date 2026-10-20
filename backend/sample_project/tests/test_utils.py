import pytest
from shop import utils
from sample_project.tests.helpers import simulate_io


def test_round_currency_standard():
    simulate_io(0.15)
    assert utils.round_currency(12.3456) == 12.35


def test_round_currency_integer():
    simulate_io(0.10)
    assert utils.round_currency(10) == 10.00


def test_round_currency_half_up():
    simulate_io(0.12)
    assert utils.round_currency(2.555) == 2.56


def test_clamp_within_bounds():
    simulate_io(0.08)
    assert utils.clamp(5.0, 1.0, 10.0) == 5.0


def test_clamp_below_low():
    simulate_io(0.05)
    assert utils.clamp(-2.0, 0.0, 10.0) == 0.0


def test_clamp_above_high():
    simulate_io(0.05)
    assert utils.clamp(15.0, 0.0, 10.0) == 10.0


def test_hash_string_deterministic():
    simulate_io(0.20)
    h1 = utils.hash_string("test-string")
    h2 = utils.hash_string("test-string")
    assert h1 == h2
    assert len(h1) == 64


def test_format_currency_usd_and_eur():
    simulate_io(0.15)
    assert utils.format_currency(29.99, "USD") == "$29.99"
    assert utils.format_currency(15.5, "EUR") == "€15.50"
    assert utils.format_currency(100.0, "GBP") == "100.00 GBP"
