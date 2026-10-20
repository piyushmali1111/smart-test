"""Management sales and tax reporting ledger."""

from typing import Any
from shop import utils, tax


def generate_sales_summary(orders: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregates revenue metrics across list of orders."""
    total_revenue = 0.0
    total_tax = 0.0
    total_discount = 0.0
    confirmed_count = 0

    for ord_obj in orders:
        if ord_obj.get("status") == "confirmed":
            confirmed_count += 1
            totals = ord_obj.get("totals", {})
            total_revenue += totals.get("grand_total", 0.0)
            total_tax += totals.get("tax", 0.0)
            total_discount += totals.get("discount", 0.0)

    avg_order_value = (
        utils.round_currency(total_revenue / confirmed_count)
        if confirmed_count > 0
        else 0.0
    )

    return {
        "confirmed_orders": confirmed_count,
        "total_revenue": utils.round_currency(total_revenue),
        "total_tax": utils.round_currency(total_tax),
        "total_discount": utils.round_currency(total_discount),
        "avg_order_value": avg_order_value,
    }


def calculate_margin_report(orders: list[dict[str, Any]]) -> dict[str, float]:
    """Estimates profit margin assuming standard 60% wholesale cost."""
    summary = generate_sales_summary(orders)
    revenue = summary["total_revenue"]
    estimated_cost = revenue * 0.60
    gross_profit = revenue - estimated_cost
    margin_pct = (gross_profit / revenue * 100.0) if revenue > 0 else 0.0
    return {
        "revenue": revenue,
        "cost": utils.round_currency(estimated_cost),
        "gross_profit": utils.round_currency(gross_profit),
        "margin_pct": utils.round_currency(margin_pct),
    }


def export_tax_ledger(orders: list[dict[str, Any]], region: str) -> dict[str, Any]:
    """Extracts jurisdiction-specific tax liabilities."""
    rate = tax.get_tax_rate(region)
    regional_tax_total = 0.0
    matching_orders = 0

    for ord_obj in orders:
        totals = ord_obj.get("totals", {})
        regional_tax_total += totals.get("tax", 0.0)
        matching_orders += 1

    return {
        "region": region.upper(),
        "statutory_rate": rate,
        "matching_orders": matching_orders,
        "collected_tax": utils.round_currency(regional_tax_total),
    }
