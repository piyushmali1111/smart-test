import pytest
from shop import auth
from sample_project.tests.helpers import simulate_io


def test_hash_password_success():
    simulate_io(0.25)
    hashed = auth.hash_password("supersecret123")
    assert len(hashed) == 64
    assert hashed != "supersecret123"


def test_hash_password_too_short():
    simulate_io(0.10)
    with pytest.raises(ValueError):
        auth.hash_password("123")


def test_verify_token_user():
    simulate_io(0.18)
    token = "tok_usr1001_user"
    res = auth.verify_token(token)
    assert res["user_id"] == "usr1001"
    assert res["role"] == "user"


def test_verify_token_invalid():
    simulate_io(0.12)
    with pytest.raises(PermissionError):
        auth.verify_token("invalid_token")


def test_check_permission_admin():
    simulate_io(0.08)
    assert auth.check_permission("admin", "refund") is True
    assert auth.check_permission("admin", "export_tax") is True
    assert auth.check_permission("admin", "view_order") is True


def test_check_permission_user():
    simulate_io(0.08)
    assert auth.check_permission("user", "view_order") is True
    assert auth.check_permission("user", "refund") is False
