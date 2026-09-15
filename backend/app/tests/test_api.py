from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_service
from app.salesforce.mock import MockSalesforceClient
from app.service import QuoteService

OPPORTUNITY = "006AX000003"  # Brightside - Compliance Suite, Qualification stage
PLATFORM = "01tAX000001"
IMPLEMENTATION = "01tAX000005"


@pytest.fixture()
def client() -> Iterator[TestClient]:
    service = QuoteService(MockSalesforceClient())
    app.dependency_overrides[get_service] = lambda: service
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_lists_opportunities_and_filters_by_search(client: TestClient) -> None:
    assert len(client.get("/api/opportunities").json()) == 4
    filtered = client.get("/api/opportunities", params={"search": "helios"}).json()
    assert [o["account_name"] for o in filtered] == ["Helios Energy"]


def test_lists_products_with_search(client: TestClient) -> None:
    products = client.get("/api/products", params={"search": "analytics"}).json()
    assert [p["sku"] for p in products] == ["PLAT-ANALYTICS"]


def test_preview_does_not_persist_a_quote(client: TestClient) -> None:
    payload = {
        "opportunity_id": OPPORTUNITY,
        "lines": [{"product_id": PLATFORM, "quantity": 20, "term_months": 12}],
    }
    assert client.post("/api/quotes/preview", json=payload).status_code == 200
    assert client.get("/api/quotes").json() == []


def test_quote_lifecycle_syncs_amount_back_to_the_opportunity(client: TestClient) -> None:
    created = client.post(
        "/api/quotes",
        json={
            "opportunity_id": OPPORTUNITY,
            "lines": [
                {"product_id": PLATFORM, "quantity": 60, "term_months": 12},
                {"product_id": IMPLEMENTATION, "quantity": 1},
            ],
        },
    ).json()
    assert created["status"] == "Draft"
    assert created["requires_approval"] is False

    quote_id = created["id"]
    synced = client.post(f"/api/quotes/{quote_id}/sync").json()
    assert synced["quote"]["status"] == "Synced to Salesforce"
    assert synced["opportunity"]["amount"] == created["totals"]["net_total"]
    assert synced["opportunity"]["stage"] == "Proposal/Price Quote"

    opportunity = client.get(f"/api/opportunities/{OPPORTUNITY}").json()
    assert opportunity["amount"] == created["totals"]["net_total"]


def test_deep_discount_requires_approval_before_sync(client: TestClient) -> None:
    created = client.post(
        "/api/quotes",
        json={
            "opportunity_id": OPPORTUNITY,
            "lines": [{"product_id": IMPLEMENTATION, "quantity": 1, "discount_percent": "35"}],
        },
    ).json()
    assert created["status"] == "Needs Approval"
    quote_id = created["id"]

    blocked = client.post(f"/api/quotes/{quote_id}/sync")
    assert blocked.status_code == 409

    assert client.post(f"/api/quotes/{quote_id}/approve").json()["status"] == "Approved"
    assert client.post(f"/api/quotes/{quote_id}/sync").status_code == 200
    assert client.post(f"/api/quotes/{quote_id}/sync").status_code == 200


def test_editing_a_synced_quote_requires_approval_again(client: TestClient) -> None:
    def payload(quantity: int) -> dict[str, object]:
        return {
            "opportunity_id": OPPORTUNITY,
            "lines": [
                {"product_id": IMPLEMENTATION, "quantity": quantity, "discount_percent": "35"}
            ],
        }

    quote_id = client.post("/api/quotes", json=payload(1)).json()["id"]
    client.post(f"/api/quotes/{quote_id}/approve")
    client.post(f"/api/quotes/{quote_id}/sync")

    reopened = client.put(f"/api/quotes/{quote_id}", json=payload(2)).json()
    assert reopened["status"] == "Needs Approval"
    assert client.post(f"/api/quotes/{quote_id}/sync").status_code == 409


def test_syncing_an_empty_quote_is_rejected(client: TestClient) -> None:
    quote_id = client.post(
        "/api/quotes", json={"opportunity_id": OPPORTUNITY, "lines": []}
    ).json()["id"]
    response = client.post(f"/api/quotes/{quote_id}/sync")
    assert response.status_code == 409
    assert "no lines" in response.json()["detail"]


def test_update_reprices_and_delete_removes_quote(client: TestClient) -> None:
    quote_id = client.post(
        "/api/quotes",
        json={
            "opportunity_id": OPPORTUNITY,
            "lines": [{"product_id": PLATFORM, "quantity": 10, "term_months": 12}],
        },
    ).json()["id"]

    updated = client.put(
        f"/api/quotes/{quote_id}",
        json={
            "opportunity_id": OPPORTUNITY,
            "lines": [{"product_id": PLATFORM, "quantity": 300, "term_months": 12}],
        },
    ).json()
    assert updated["lines"][0]["volume_discount_percent"] == "10.00"

    assert client.delete(f"/api/quotes/{quote_id}").status_code == 204
    assert client.get(f"/api/quotes/{quote_id}").status_code == 404


def test_unknown_references_return_404(client: TestClient) -> None:
    missing_product = client.post(
        "/api/quotes",
        json={"opportunity_id": OPPORTUNITY, "lines": [{"product_id": "nope", "quantity": 1}]},
    )
    assert missing_product.status_code == 404
    assert client.get("/api/opportunities/006NOPE").status_code == 404
