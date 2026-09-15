from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from ..models import Account, Opportunity, Product


class SalesforceClient(ABC):
    """Interface every Salesforce backend implements.

    The mock implementation keeps everything in memory; a real implementation
    talks to the REST API. Nothing outside this package should depend on which
    one is in use.
    """

    @abstractmethod
    def list_opportunities(self, search: str | None = None) -> list[Opportunity]: ...

    @abstractmethod
    def get_opportunity(self, opportunity_id: str) -> Opportunity | None: ...

    @abstractmethod
    def get_account(self, account_id: str) -> Account | None: ...

    @abstractmethod
    def list_products(self, search: str | None = None) -> list[Product]: ...

    @abstractmethod
    def get_product(self, product_id: str) -> Product | None: ...

    @abstractmethod
    def push_quote_amount(
        self, opportunity_id: str, amount: Decimal, quote_name: str
    ) -> Opportunity: ...
