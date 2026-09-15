# Breeze CPQ

A quoting / CPQ app for Salesforce opportunities: pick an opportunity, build a quote from the
product catalog, watch pricing recalculate live, and push the result back to the opportunity.

Salesforce access sits behind the `SalesforceClient` interface. The shipped implementation is an
in-memory mock seeded with demo accounts, opportunities and a price book, so the app runs with no
Salesforce org.

## Layout

```
backend/   FastAPI service: pricing engine, quote lifecycle, Salesforce client
frontend/  React + TypeScript (Vite) UI
```

## Running locally

Backend (port 8000):

```bash
cd backend
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Frontend (port 5173, proxies `/api` to the backend):

```bash
cd frontend
npm install
npm run dev
```

## Checks

```bash
cd backend && source .venv/bin/activate && pytest && ruff check . && mypy app
cd frontend && npm run lint && npm run typecheck && npm run build
```

## Pricing rules

- Recurring products are priced per unit per month and multiplied by the quote term; one-time
  products ignore the term.
- Volume tiers come from the price book; the highest matching tier applies.
- Volume and manual line discounts compound (`net = list × (1 − volume) × (1 − manual)`); manual
  line discounts are capped at 40%.
- A quote-level discount applies on top of every line.
- An effective discount above 20% puts the quote in **Needs Approval**; it cannot sync to
  Salesforce until approved.
- Syncing writes the net total to the opportunity's amount and advances early-stage opportunities
  to Proposal/Price Quote.

## Swapping in a real Salesforce org

Implement `SalesforceClient` (`backend/app/salesforce/base.py`) against the Salesforce REST API and
register it in `build_salesforce_client()`, selected by the `CPQ_SALESFORCE_BACKEND` environment
variable. The API, pricing engine and UI need no changes: the mock and real clients return the same
`Opportunity`, `Product` and `Account` models, and quote writeback goes through
`push_quote_amount()`.

Credentials for a real client (Connected App consumer key/secret, or a username/token pair) should
be read from environment variables; none are required today.
