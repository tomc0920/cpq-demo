import { useCallback, useEffect, useMemo, useState } from "react";

import { api } from "./api";
import { OpportunityList } from "./components/OpportunityList";
import { ProductCatalog } from "./components/ProductCatalog";
import { QuoteLinesTable } from "./components/QuoteLinesTable";
import { QuoteSummary } from "./components/QuoteSummary";
import { money, shortDate } from "./format";
import type { Opportunity, Product, Quote, QuoteInput, QuoteLineInput } from "./types";

export default function App() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Opportunity | null>(null);

  const [lines, setLines] = useState<QuoteLineInput[]>([]);
  const [quoteDiscount, setQuoteDiscount] = useState("0");
  const [preview, setPreview] = useState<Quote | null>(null);
  const [savedQuote, setSavedQuote] = useState<Quote | null>(null);
  const [savedPayload, setSavedPayload] = useState<string | null>(null);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listProducts().then(setProducts).catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      api
        .listOpportunities(search)
        .then((results) => {
          setOpportunities(results);
          setSelected((current) =>
            current ? (results.find((o) => o.id === current.id) ?? current) : (results[0] ?? null),
          );
        })
        .catch((err: Error) => setError(err.message));
    }, 200);
    return () => clearTimeout(timer);
  }, [search]);

  const opportunityId = selected?.id ?? null;
  const payload: QuoteInput | null = useMemo(
    () =>
      opportunityId
        ? { opportunity_id: opportunityId, lines, quote_discount_percent: quoteDiscount || "0" }
        : null,
    [opportunityId, lines, quoteDiscount],
  );

  useEffect(() => {
    if (!payload) return;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      api
        .previewQuote(payload, controller.signal)
        .then((quote) => {
          setPreview(quote);
          setError(null);
        })
        .catch((err: Error) => {
          if (err.name !== "AbortError") setError(err.message);
        });
    }, 150);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [payload]);

  const selectOpportunity = useCallback((opportunity: Opportunity) => {
    setSelected(opportunity);
    setLines([]);
    setQuoteDiscount("0");
    setPreview(null);
    setSavedQuote(null);
    setSavedPayload(null);
    setError(null);
  }, []);

  const addProduct = (product: Product) =>
    setLines((current) => [
      ...current,
      {
        product_id: product.id,
        quantity: product.charge_type === "recurring" ? 25 : 1,
        term_months: 12,
        discount_percent: "0",
      },
    ]);

  const changeLine = (index: number, patch: Partial<QuoteLineInput>) =>
    setLines((current) => current.map((line, i) => (i === index ? { ...line, ...patch } : line)));

  const removeLine = (index: number) =>
    setLines((current) => current.filter((_, i) => i !== index));

  const run = async (action: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const saveQuote = () =>
    run(async () => {
      if (!payload) return;
      const quote = savedQuote
        ? await api.updateQuote(savedQuote.id, payload)
        : await api.createQuote(payload);
      setSavedQuote(quote);
      setSavedPayload(JSON.stringify(payload));
      setPreview(quote);
    });

  const approveQuote = () =>
    run(async () => {
      if (!savedQuote) return;
      setSavedQuote(await api.approveQuote(savedQuote.id));
    });

  const syncQuote = () =>
    run(async () => {
      if (!savedQuote) return;
      const result = await api.syncQuote(savedQuote.id);
      setSavedQuote(result.quote);
      setPreview(result.quote);
      setSelected(result.opportunity);
      setOpportunities((current) =>
        current.map((o) => (o.id === result.opportunity.id ? result.opportunity : o)),
      );
    });

  return (
    <div className="layout">
      <header className="topbar">
        <div>
          <h1>Breeze CPQ</h1>
          <span className="muted small">Quote builder for Salesforce opportunities</span>
        </div>
        <span className="pill">Mock Salesforce org</span>
      </header>

      <div className="body">
        <OpportunityList
          opportunities={opportunities}
          selectedId={selected?.id ?? null}
          search={search}
          onSearch={setSearch}
          onSelect={selectOpportunity}
        />

        <main className="content">
          {error && <p className="banner error">{error}</p>}

          {selected ? (
            <>
              <section className="card opportunity-header">
                <div>
                  <h2>{selected.name}</h2>
                  <span className="muted">
                    {selected.account_name} · {selected.owner_name} · closes{" "}
                    {shortDate(selected.close_date)}
                  </span>
                </div>
                <div className="opportunity-figures">
                  <span className="stage">{selected.stage}</span>
                  <span className="amount">{money(selected.amount)}</span>
                  <span className="muted small">
                    {savedQuote ? `Quote ${savedQuote.id} · ${savedQuote.status}` : "No saved quote"}
                  </span>
                </div>
              </section>

              <div className="columns">
                <div className="column">
                  <ProductCatalog
                    products={products}
                    onAdd={addProduct}
                    addedProductIds={lines.map((line) => line.product_id)}
                  />
                  <QuoteLinesTable
                    lines={lines}
                    pricedLines={preview?.lines ?? []}
                    products={products}
                    onChange={changeLine}
                    onRemove={removeLine}
                  />
                </div>
                <QuoteSummary
                  quote={preview}
                  dirty={payload !== null && JSON.stringify(payload) !== savedPayload}
                  quoteDiscount={quoteDiscount}
                  onQuoteDiscountChange={setQuoteDiscount}
                  savedQuote={savedQuote}
                  busy={busy}
                  onSave={saveQuote}
                  onApprove={approveQuote}
                  onSync={syncQuote}
                />
              </div>
            </>
          ) : (
            <p className="empty">Select an opportunity to build a quote.</p>
          )}
        </main>
      </div>
    </div>
  );
}
