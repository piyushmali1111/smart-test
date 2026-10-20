"""Tax computation and regional exemptions."""

from shop import utils

REGIONAL_TAX_RATES: dict[str, float] = {
    "CA": 0.0825,
    "NY": 0.08875,
    "TX": 0.0625,
    "EU": 0.20,
    "DEFAULT": 0.05,
}


def get_tax_rate(region: str) -> float:
    """Returns statutory tax rate for a geographical region code."""
    reg = region.upper() if region else "DEFAULT"
    return REGIONAL_TAX_RATES.get(reg, REGIONAL_TAX_RATES["DEFAULT"])


def calculate_sales_tax(subtotal: float, region: str) -> float:
    """Calculates sales tax amount on subtotal for given region."""
    if subtotal <= 0.0:
        return 0.0
    rate = get_tax_rate(region)
    raw_tax = subtotal * rate
    return utils.round_currency(raw_tax)


def apply_tax_exemptions(tax_amount: float, is_exempt: bool) -> float:
    """Zeroes out tax amount if purchaser qualifies for tax exemption."""
    if is_exempt:
        return 0.0
    return utils.round_currency(tax_amount)
