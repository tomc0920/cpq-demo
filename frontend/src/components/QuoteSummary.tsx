import { money, percent } from "../format";
import type { Quote } from "../types";

interface Props {
  quote: Quote | null;
  dirty: boolean;
  quoteDiscount: string;
  onQuoteDiscountChange: (value: string) => void;
  savedQuote: Quote | null;
  busy: boolean;
  onSave: () => void;
  onApprove: () => void;
  onSync: () => void;
}

export function QuoteSummary({
  quote,
  dirty,
  quoteDiscount,
  onQuoteDiscountChange,
  savedQuote,
  busy,
  onSave,
  onApprove,
  onSync,
}: Props) {
  const totals = quote?.totals;
  const needsApproval = Boolean(quote?.requires_approval);
  const approved = savedQuote?.status === "Approved" || savedQuote?.status === "Synced to Salesforce";
  const canSync = Boolean(savedQuote) && !dirty && (!needsApproval || approved);

  return (
    <section className="card summary">
      <h3>Quote summary</h3>

      <label className="field">
        <span>Quote-level discount</span>
        <div className="discount-input">
          <input
            type="number"
            min={0}
            max={100}
            value={quoteDiscount}
            onChange={(event) => onQuoteDiscountChange(event.target.value || "0")}
          />
          <span className="muted">%</span>
        </div>
      </label>

      <dl className="totals">
        <div>
          <dt>List total</dt>
          <dd>{totals ? money(totals.list_total) : "—"}</dd>
        </div>
        <div>
          <dt>Discount</dt>
          <dd className="negative">{totals ? `− ${money(totals.discount_total)}` : "—"}</dd>
        </div>
        <div>
          <dt>One-time</dt>
          <dd>{totals ? money(totals.one_time_total) : "—"}</dd>
        </div>
        <div>
          <dt>Recurring</dt>
          <dd>{totals ? money(totals.recurring_total) : "—"}</dd>
        </div>
        <div>
          <dt>ARR</dt>
          <dd>{totals ? money(totals.annual_recurring_revenue) : "—"}</dd>
        </div>
        <div className="grand">
          <dt>Net total</dt>
          <dd>{totals ? money(totals.net_total) : "—"}</dd>
        </div>
      </dl>

      {totals && (
        <p className="muted small">
          Effective discount {percent(totals.effective_discount_percent)}
        </p>
      )}

      {quote?.approval_reason && (!approved || dirty) && (
        <p className="banner warning">{quote.approval_reason}</p>
      )}

      {savedQuote && dirty && (
        <p className="banner warning">
          Unsaved changes — save the quote to sync these totals to Salesforce.
        </p>
      )}

      {savedQuote?.status === "Synced to Salesforce" && !dirty && (
        <p className="banner success">
          {savedQuote.id} synced — opportunity amount set to {money(savedQuote.totals.net_total)}.
        </p>
      )}

      <div className="actions">
        <button type="button" onClick={onSave} disabled={busy || !quote}>
          {savedQuote ? "Save changes" : "Save quote"}
        </button>
        {needsApproval && (!approved || dirty) && (
          <button type="button" onClick={onApprove} disabled={busy || !savedQuote || dirty}>
            Approve discount
          </button>
        )}
        <button type="button" className="primary" onClick={onSync} disabled={busy || !canSync}>
          Sync to Salesforce
        </button>
      </div>
      {!savedQuote && <p className="muted small">Save the quote before syncing it.</p>}
    </section>
  );
}
