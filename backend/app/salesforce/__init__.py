from __future__ import annotations

import os

from .base import SalesforceClient
from .mock import MockSalesforceClient

__all__ = ["SalesforceClient", "MockSalesforceClient", "build_salesforce_client"]


def build_salesforce_client() -> SalesforceClient:
    """Pick the Salesforce backend from ``CPQ_SALESFORCE_BACKEND``.

    Only ``mock`` ships today. A REST-backed client implementing
    ``SalesforceClient`` can be registered here without touching the API or
    pricing layers.
    """
    backend = os.getenv("CPQ_SALESFORCE_BACKEND", "mock").lower()
    if backend == "mock":
        return MockSalesforceClient()
    raise ValueError(
        f"Unknown Salesforce backend {backend!r}. Supported backends: 'mock'."
    )
