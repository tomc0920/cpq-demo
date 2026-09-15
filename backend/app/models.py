from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class Account(BaseModel):
    id: str
    name: str
    industry: str
    billing_city: str


class OpportunityStage(str, Enum):
    prospecting = "Prospecting"
    qualification = "Qualification"
    proposal = "Proposal/Price Quote"
    negotiation = "Negotiation/Review"
    closed_won = "Closed Won"
    closed_lost = "Closed Lost"


class Opportunity(BaseModel):
    id: str
    name: str
    account_id: str
    account_name: str
    stage: OpportunityStage
    amount: Decimal
    close_date: date
    owner_name: str


class ChargeType(str, Enum):
    one_time = "one_time"
    recurring = "recurring"


class VolumeTier(BaseModel):
    min_quantity: int
    discount_percent: Decimal


class Product(BaseModel):
    id: str
    name: str
    sku: str
    family: str
    description: str
    list_price: Decimal
    charge_type: ChargeType
    volume_tiers: list[VolumeTier] = Field(default_factory=list)


class QuoteStatus(str, Enum):
    draft = "Draft"
    needs_approval = "Needs Approval"
    approved = "Approved"
    synced = "Synced to Salesforce"


class QuoteLineInput(BaseModel):
    product_id: str
    quantity: int = Field(ge=1)
    term_months: int = Field(default=12, ge=1, le=60)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class QuoteLine(BaseModel):
    id: str
    product_id: str
    name: str
    sku: str
    family: str
    charge_type: ChargeType
    quantity: int
    term_months: int
    list_price: Decimal
    volume_discount_percent: Decimal
    discount_percent: Decimal
    effective_discount_percent: Decimal
    net_unit_price: Decimal
    list_total: Decimal
    net_total: Decimal


class QuoteTotals(BaseModel):
    list_total: Decimal
    discount_total: Decimal
    net_total: Decimal
    one_time_total: Decimal
    recurring_total: Decimal
    annual_recurring_revenue: Decimal
    effective_discount_percent: Decimal


class QuoteInput(BaseModel):
    opportunity_id: str
    name: str | None = None
    lines: list[QuoteLineInput] = Field(default_factory=list)
    quote_discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    expires_on: date | None = None


class Quote(BaseModel):
    id: str
    name: str
    opportunity_id: str
    opportunity_name: str
    account_name: str
    status: QuoteStatus
    lines: list[QuoteLine]
    quote_discount_percent: Decimal
    totals: QuoteTotals
    requires_approval: bool
    approval_reason: str | None
    expires_on: date | None
    created_at: datetime
    updated_at: datetime
    synced_at: datetime | None = None


class SyncResult(BaseModel):
    quote: Quote
    opportunity: Opportunity
