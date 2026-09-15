from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import Opportunity, Product, Quote, QuoteInput, SyncResult
from .salesforce import build_salesforce_client
from .service import NotFoundError, QuoteService

app = FastAPI(title="CPQ Quoting API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CPQ_CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

_service = QuoteService(build_salesforce_client())


def get_service() -> QuoteService:
    return _service


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/opportunities", response_model=list[Opportunity])
def list_opportunities(
    search: str | None = Query(default=None),
    service: QuoteService = Depends(get_service),
) -> list[Opportunity]:
    return service.salesforce.list_opportunities(search)


@app.get("/api/opportunities/{opportunity_id}", response_model=Opportunity)
def get_opportunity(
    opportunity_id: str, service: QuoteService = Depends(get_service)
) -> Opportunity:
    opportunity = service.salesforce.get_opportunity(opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@app.get("/api/products", response_model=list[Product])
def list_products(
    search: str | None = Query(default=None),
    service: QuoteService = Depends(get_service),
) -> list[Product]:
    return service.salesforce.list_products(search)


@app.post("/api/quotes/preview", response_model=Quote)
def preview_quote(payload: QuoteInput, service: QuoteService = Depends(get_service)) -> Quote:
    try:
        return service.preview(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/quotes", response_model=list[Quote])
def list_quotes(
    opportunity_id: str | None = Query(default=None),
    service: QuoteService = Depends(get_service),
) -> list[Quote]:
    return service.list(opportunity_id)


@app.post("/api/quotes", response_model=Quote, status_code=201)
def create_quote(payload: QuoteInput, service: QuoteService = Depends(get_service)) -> Quote:
    try:
        return service.create(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/quotes/{quote_id}", response_model=Quote)
def get_quote(quote_id: str, service: QuoteService = Depends(get_service)) -> Quote:
    try:
        return service.get(quote_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/api/quotes/{quote_id}", response_model=Quote)
def update_quote(
    quote_id: str, payload: QuoteInput, service: QuoteService = Depends(get_service)
) -> Quote:
    try:
        return service.update(quote_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/api/quotes/{quote_id}", status_code=204)
def delete_quote(quote_id: str, service: QuoteService = Depends(get_service)) -> None:
    try:
        service.delete(quote_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/quotes/{quote_id}/approve", response_model=Quote)
def approve_quote(quote_id: str, service: QuoteService = Depends(get_service)) -> Quote:
    try:
        return service.approve(quote_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/quotes/{quote_id}/sync", response_model=SyncResult)
def sync_quote(quote_id: str, service: QuoteService = Depends(get_service)) -> SyncResult:
    try:
        return service.sync(quote_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
