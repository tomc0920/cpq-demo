from __future__ import annotations

from datetime import date
from decimal import Decimal

from ..models import (
    Account,
    ChargeType,
    Opportunity,
    OpportunityStage,
    Product,
    VolumeTier,
)
from .base import SalesforceClient


def _seed_accounts() -> list[Account]:
    return [
        Account(id="001AX000001", name="Northwind Logistics", industry="Transportation",
                billing_city="Chicago"),
        Account(id="001AX000002", name="Helios Energy", industry="Energy", billing_city="Houston"),
        Account(id="001AX000003", name="Brightside Health", industry="Healthcare",
                billing_city="Boston"),
        Account(id="001AX000004", name="Lumen Retail Group", industry="Retail",
                billing_city="Seattle"),
    ]


def _seed_opportunities() -> list[Opportunity]:
    return [
        Opportunity(
            id="006AX000001",
            name="Northwind - Platform Expansion",
            account_id="001AX000001",
            account_name="Northwind Logistics",
            stage=OpportunityStage.proposal,
            amount=Decimal("185000.00"),
            close_date=date(2026, 3, 31),
            owner_name="Dana Whitfield",
        ),
        Opportunity(
            id="006AX000002",
            name="Helios - Field Ops Rollout",
            account_id="001AX000002",
            account_name="Helios Energy",
            stage=OpportunityStage.negotiation,
            amount=Decimal("92000.00"),
            close_date=date(2026, 1, 15),
            owner_name="Marcus Reed",
        ),
        Opportunity(
            id="006AX000003",
            name="Brightside - Compliance Suite",
            account_id="001AX000003",
            account_name="Brightside Health",
            stage=OpportunityStage.qualification,
            amount=Decimal("47500.00"),
            close_date=date(2026, 5, 29),
            owner_name="Priya Raman",
        ),
        Opportunity(
            id="006AX000004",
            name="Lumen Retail - Store Analytics",
            account_id="001AX000004",
            account_name="Lumen Retail Group",
            stage=OpportunityStage.prospecting,
            amount=Decimal("128000.00"),
            close_date=date(2026, 6, 30),
            owner_name="Dana Whitfield",
        ),
    ]


def _seed_products() -> list[Product]:
    return [
        Product(
            id="01tAX000001",
            name="Platform Subscription",
            sku="PLAT-BASE",
            family="Platform",
            description="Core platform access, billed per user per month.",
            list_price=Decimal("45.00"),
            charge_type=ChargeType.recurring,
            volume_tiers=[
                VolumeTier(min_quantity=50, discount_percent=Decimal("5")),
                VolumeTier(min_quantity=250, discount_percent=Decimal("10")),
                VolumeTier(min_quantity=1000, discount_percent=Decimal("15")),
            ],
        ),
        Product(
            id="01tAX000002",
            name="Advanced Analytics",
            sku="PLAT-ANALYTICS",
            family="Platform",
            description="Dashboards, cohort reporting and data export.",
            list_price=Decimal("18.00"),
            charge_type=ChargeType.recurring,
            volume_tiers=[
                VolumeTier(min_quantity=100, discount_percent=Decimal("7.5")),
                VolumeTier(min_quantity=500, discount_percent=Decimal("12.5")),
            ],
        ),
        Product(
            id="01tAX000003",
            name="API Gateway Add-on",
            sku="ADDON-API",
            family="Add-on",
            description="Elevated API rate limits and webhook delivery.",
            list_price=Decimal("12.00"),
            charge_type=ChargeType.recurring,
            volume_tiers=[VolumeTier(min_quantity=200, discount_percent=Decimal("10"))],
        ),
        Product(
            id="01tAX000004",
            name="Premium Support",
            sku="SUP-PREMIUM",
            family="Support",
            description="24/7 support with a one-hour response SLA.",
            list_price=Decimal("9.00"),
            charge_type=ChargeType.recurring,
        ),
        Product(
            id="01tAX000005",
            name="Implementation Services",
            sku="SVC-IMPL",
            family="Services",
            description="Guided onboarding and data migration, billed per engagement.",
            list_price=Decimal("15000.00"),
            charge_type=ChargeType.one_time,
        ),
        Product(
            id="01tAX000006",
            name="Admin Training Workshop",
            sku="SVC-TRAINING",
            family="Services",
            description="Two-day workshop for platform administrators.",
            list_price=Decimal("4500.00"),
            charge_type=ChargeType.one_time,
            volume_tiers=[VolumeTier(min_quantity=3, discount_percent=Decimal("10"))],
        ),
    ]


def _matches(search: str | None, *fields: str) -> bool:
    if not search:
        return True
    needle = search.lower()
    return any(needle in field.lower() for field in fields)


class MockSalesforceClient(SalesforceClient):
    """In-memory stand-in for a Salesforce org, seeded with demo CPQ data."""

    def __init__(self) -> None:
        self._accounts = {a.id: a for a in _seed_accounts()}
        self._opportunities = {o.id: o for o in _seed_opportunities()}
        self._products = {p.id: p for p in _seed_products()}

    def list_opportunities(self, search: str | None = None) -> list[Opportunity]:
        return [
            o
            for o in self._opportunities.values()
            if _matches(search, o.name, o.account_name, o.owner_name)
        ]

    def get_opportunity(self, opportunity_id: str) -> Opportunity | None:
        return self._opportunities.get(opportunity_id)

    def get_account(self, account_id: str) -> Account | None:
        return self._accounts.get(account_id)

    def list_products(self, search: str | None = None) -> list[Product]:
        return [
            p
            for p in self._products.values()
            if _matches(search, p.name, p.sku, p.family, p.description)
        ]

    def get_product(self, product_id: str) -> Product | None:
        return self._products.get(product_id)

    def push_quote_amount(
        self, opportunity_id: str, amount: Decimal, quote_name: str
    ) -> Opportunity:
        opportunity = self._opportunities[opportunity_id]
        updated = opportunity.model_copy(
            update={
                "amount": amount,
                "stage": (
                    OpportunityStage.proposal
                    if opportunity.stage
                    in (OpportunityStage.prospecting, OpportunityStage.qualification)
                    else opportunity.stage
                ),
            }
        )
        self._opportunities[opportunity_id] = updated
        return updated
