from __future__ import annotations

import uuid
from datetime import datetime, timezone

from .models import Quote, QuoteInput, QuoteStatus, SyncResult
from .pricing import approval_reason, price_line, summarize
from .salesforce import SalesforceClient


class NotFoundError(Exception):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


class QuoteService:
    """Builds and stores quotes; Salesforce access goes through the injected client."""

    def __init__(self, salesforce: SalesforceClient) -> None:
        self.salesforce = salesforce
        self._quotes: dict[str, Quote] = {}

    def _build(self, quote_id: str, payload: QuoteInput, existing: Quote | None) -> Quote:
        opportunity = self.salesforce.get_opportunity(payload.opportunity_id)
        if opportunity is None:
            raise NotFoundError(f"Opportunity {payload.opportunity_id} not found")

        lines = []
        for index, line in enumerate(payload.lines, start=1):
            product = self.salesforce.get_product(line.product_id)
            if product is None:
                raise NotFoundError(f"Product {line.product_id} not found")
            lines.append(price_line(f"{quote_id}-L{index}", product, line))

        totals = summarize(lines, payload.quote_discount_percent)
        reason = approval_reason(totals)
        status = QuoteStatus.needs_approval if reason else QuoteStatus.draft

        return Quote(
            id=quote_id,
            name=payload.name or f"{opportunity.name} Quote",
            opportunity_id=opportunity.id,
            opportunity_name=opportunity.name,
            account_name=opportunity.account_name,
            status=status,
            lines=lines,
            quote_discount_percent=payload.quote_discount_percent,
            totals=totals,
            requires_approval=reason is not None,
            approval_reason=reason,
            expires_on=payload.expires_on,
            created_at=existing.created_at if existing else _now(),
            updated_at=_now(),
        )

    def preview(self, payload: QuoteInput) -> Quote:
        return self._build("preview", payload, existing=None)

    def create(self, payload: QuoteInput) -> Quote:
        quote = self._build(f"QT-{uuid.uuid4().hex[:8].upper()}", payload, existing=None)
        self._quotes[quote.id] = quote
        return quote

    def update(self, quote_id: str, payload: QuoteInput) -> Quote:
        existing = self.get(quote_id)
        quote = self._build(quote_id, payload, existing=existing)
        self._quotes[quote_id] = quote
        return quote

    def get(self, quote_id: str) -> Quote:
        quote = self._quotes.get(quote_id)
        if quote is None:
            raise NotFoundError(f"Quote {quote_id} not found")
        return quote

    def list(self, opportunity_id: str | None = None) -> list[Quote]:
        quotes = list(self._quotes.values())
        if opportunity_id:
            quotes = [q for q in quotes if q.opportunity_id == opportunity_id]
        return sorted(quotes, key=lambda q: q.updated_at, reverse=True)

    def delete(self, quote_id: str) -> None:
        if self._quotes.pop(quote_id, None) is None:
            raise NotFoundError(f"Quote {quote_id} not found")

    def approve(self, quote_id: str) -> Quote:
        quote = self.get(quote_id)
        approved = quote.model_copy(update={"status": QuoteStatus.approved, "updated_at": _now()})
        self._quotes[quote_id] = approved
        return approved

    def sync(self, quote_id: str) -> SyncResult:
        quote = self.get(quote_id)
        if not quote.lines:
            raise ValueError("Quote has no lines, so it cannot be synced to Salesforce")
        if quote.requires_approval and quote.status not in (
            QuoteStatus.approved,
            QuoteStatus.synced,
        ):
            raise ValueError("Quote needs approval before it can be synced to Salesforce")

        opportunity = self.salesforce.push_quote_amount(
            quote.opportunity_id, quote.totals.net_total, quote.name
        )
        synced = quote.model_copy(
            update={
                "status": QuoteStatus.synced,
                "synced_at": _now(),
                "updated_at": _now(),
            }
        )
        self._quotes[quote_id] = synced
        return SyncResult(quote=synced, opportunity=opportunity)
