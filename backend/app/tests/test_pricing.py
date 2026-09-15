from decimal import Decimal

from app.models import QuoteLine, QuoteLineInput
from app.pricing import MAX_LINE_DISCOUNT_PERCENT, price_line, summarize
from app.salesforce.mock import MockSalesforceClient

sf = MockSalesforceClient()
PLATFORM = "01tAX000001"  # recurring, $45/user/month, tiers at 50/250/1000
IMPLEMENTATION = "01tAX000005"  # one-time, $15,000
TRAINING = "01tAX000006"  # one-time, $4,500, 10% at qty 3


def price(
    product_id: str,
    quantity: int = 1,
    term_months: int = 12,
    discount_percent: Decimal = Decimal("0"),
) -> QuoteLine:
    product = sf.get_product(product_id)
    assert product is not None
    return price_line(
        "L1",
        product,
        QuoteLineInput(
            product_id=product_id,
            quantity=quantity,
            term_months=term_months,
            discount_percent=discount_percent,
        ),
    )


def test_recurring_line_multiplies_by_term() -> None:
    line = price(PLATFORM, quantity=10, term_months=12)
    assert line.list_total == Decimal("5400.00")
    assert line.net_total == Decimal("5400.00")
    assert line.volume_discount_percent == Decimal("0.00")


def test_one_time_line_ignores_term() -> None:
    line = price(IMPLEMENTATION, quantity=1, term_months=36)
    assert line.net_total == Decimal("15000.00")


def test_volume_tier_applies_highest_matching_tier() -> None:
    line = price(PLATFORM, quantity=300, term_months=12)
    assert line.volume_discount_percent == Decimal("10.00")
    assert line.net_unit_price == Decimal("40.50")


def test_volume_and_manual_discounts_compound() -> None:
    line = price(TRAINING, quantity=3, discount_percent=Decimal("10"))
    assert line.effective_discount_percent == Decimal("19.00")
    assert line.net_unit_price == Decimal("3645.00")


def test_manual_discount_is_capped() -> None:
    line = price(IMPLEMENTATION, quantity=1, discount_percent=Decimal("90"))
    assert line.discount_percent == MAX_LINE_DISCOUNT_PERCENT
    assert line.net_total == Decimal("9000.00")


def test_totals_split_recurring_and_one_time_and_compute_arr() -> None:
    lines = [
        price(PLATFORM, quantity=100, term_months=24),
        price(IMPLEMENTATION, quantity=1),
    ]
    totals = summarize(lines, Decimal("0"))
    # 100 users * $45 * 24 months, 5% volume tier => 102,600 recurring
    assert totals.recurring_total == Decimal("102600.00")
    assert totals.one_time_total == Decimal("15000.00")
    assert totals.annual_recurring_revenue == Decimal("51300.00")
    assert totals.net_total == Decimal("117600.00")


def test_quote_level_discount_applies_on_top_of_line_discounts() -> None:
    lines = [price(IMPLEMENTATION, quantity=1, discount_percent=Decimal("10"))]
    totals = summarize(lines, Decimal("10"))
    assert totals.net_total == Decimal("12150.00")
    assert totals.effective_discount_percent == Decimal("19.00")


def test_empty_quote_has_zero_totals() -> None:
    totals = summarize([], Decimal("25"))
    assert totals.net_total == Decimal("0.00")
    assert totals.effective_discount_percent == Decimal("0.00")
