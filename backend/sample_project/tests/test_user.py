import pytest
from shop import user
from sample_project.tests.helpers import simulate_io


def test_get_user_profile_exists():
    simulate_io(0.15)
    prof = user.get_user_profile("usr_101")
    assert prof["name"] == "Alice"
    assert prof["loyalty_tier"] == "gold"


def test_get_user_profile_missing():
    simulate_io(0.10)
    with pytest.raises(KeyError):
        user.get_user_profile("usr_nonexistent")


def test_calculate_loyalty_tier_platinum():
    simulate_io(0.08)
    assert user.calculate_loyalty_tier(6000.0) == "platinum"


def test_calculate_loyalty_tier_gold():
    simulate_io(0.08)
    assert user.calculate_loyalty_tier(1500.0) == "gold"


def test_calculate_loyalty_tier_silver_bronze():
    simulate_io(0.08)
    assert user.calculate_loyalty_tier(300.0) == "silver"
    assert user.calculate_loyalty_tier(50.0) == "bronze"


def test_can_apply_vip_discount():
    simulate_io(0.12)
    assert user.can_apply_vip_discount("usr_vip") is True
    assert user.can_apply_vip_discount("usr_101") is True
    assert user.can_apply_vip_discount("usr_103") is False
    assert user.can_apply_vip_discount("usr_unknown") is False
