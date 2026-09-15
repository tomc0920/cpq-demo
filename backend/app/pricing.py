from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from .models import (
    ChargeType,
    Product,
    QuoteLine,
    QuoteLineInput,
    QuoteTotals,
)

MAX_LINE_DISCOUNT_PERCENT = Decimal("40")
APPROVAL_DISCOUNT_THRESHOLD_PERCENT = Decimal("20")

CENTS = Decimal("0.01")
PERCENT = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def _percent(value: Decimal) -> Decimal:
    return value.quantize(PERCENT, rounding=ROUND_HALF_UP)


def volume_discount_percent(product: Product, quantity: int) -> Decimal:
    applicable = [t.discount_percent for t in product.volume_tiers if quantity >= t.min_quantity]
    return max(applicable, default=Decimal("0"))


def _billing_periods(charge_type: ChargeType, term_months: int) -> Decimal:
    """A recurring product is priced per unit per month; a one-time product ignores the term."""
    if charge_type is ChargeType.recurring:
        return Decimal(term_months)
    return Decimal(1)


def price_line(line_id: str, product: Product, line: QuoteLineInput) -> QuoteLine:
    volume = volume_discount_percent(product, line.quantity)
    manual = min(line.discount_percent, MAX_LINE_DISCOUNT_PERCENT)
    remaining = (1 - volume / 100) * (1 - manual / 100)
    effective = (1 - remaining) * 100

    periods = _billing_periods(product.charge_type, line.term_months)
    net_unit_price = product.list_price * remaining
    list_total = product.list_price * line.quantity * periods
    net_total = net_unit_price * line.quantity * periods

    return QuoteLine(
        id=line_id,
        product_id=product.id,
        name=product.name,
        sku=product.sku,
        family=product.family,
        charge_type=product.charge_type,
        quantity=line.quantity,
        term_months=line.term_months,
        list_price=product.list_price,
        volume_discount_percent=_percent(volume),
        discount_percent=_percent(manual),
        effective_discount_percent=_percent(effective),
        net_unit_price=_money(net_unit_price),
        list_total=_money(list_total),
        net_total=_money(net_total),
    )


def summarize(lines: list[QuoteLine], quote_discount_percent: Decimal) -> QuoteTotals:
    quote_multiplier = 1 - quote_discount_percent / 100
    list_total = sum((line.list_total for line in lines), Decimal("0"))
    net_total = sum((line.net_total for line in lines), Decimal("0")) * quote_multiplier
    one_time = sum(
        (line.net_total for line in lines if line.charge_type is ChargeType.one_time),
        Decimal("0"),
    ) * quote_multiplier
    recurring = net_total - one_time

    arr = Decimal("0")
    for line in lines:
        if line.charge_type is ChargeType.recurring:
            monthly = line.net_total / Decimal(line.term_months)
            arr += monthly * 12 * quote_multiplier

    effective = Decimal("0") if list_total == 0 else (1 - net_total / list_total) * 100

    return QuoteTotals(
        list_total=_money(list_total),
        discount_total=_money(list_total - net_total),
        net_total=_money(net_total),
        one_time_total=_money(one_time),
        recurring_total=_money(recurring),
        annual_recurring_revenue=_money(arr),
        effective_discount_percent=_percent(effective),
    )


def approval_reason(totals: QuoteTotals) -> str | None:
    if totals.effective_discount_percent > APPROVAL_DISCOUNT_THRESHOLD_PERCENT:
        return (
            f"Effective discount {totals.effective_discount_percent}% exceeds the "
            f"{APPROVAL_DISCOUNT_THRESHOLD_PERCENT}% approval threshold."
        )
    return None
