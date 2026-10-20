import pytest
from shop import notification
from sample_project.tests.helpers import simulate_io


def test_format_order_email():
    simulate_io(0.12)
    items = [{"sku": "SKU-1001", "quantity": 2}]
    email = notification.format_order_email("ord_123", 45.0, items)
    assert "ord_123" in email
    assert "$45.00" in email
    assert "SKU-1001: 2x" in email


def test_send_email_valid():
    simulate_io(0.10)
    assert notification.send_email("alice@example.com", "Welcome", "Hello!") is True


def test_send_email_invalid():
    simulate_io(0.08)
    assert notification.send_email("invalid_email", "Subject", "Body") is False


def test_send_sms_valid():
    simulate_io(0.10)
    assert notification.send_sms("+15551234567", "Your code is 1234") is True


def test_send_sms_invalid():
    simulate_io(0.08)
    assert notification.send_sms("123", "Short") is False


def test_log_audit_event():
    simulate_io(0.08)
    initial_len = len(notification.NOTIFICATION_AUDIT_LOG)
    notification.log_audit_event("TEST_EVENT", {"foo": "bar"})
    assert len(notification.NOTIFICATION_AUDIT_LOG) == initial_len + 1
    assert notification.NOTIFICATION_AUDIT_LOG[-1]["event"] == "TEST_EVENT"
