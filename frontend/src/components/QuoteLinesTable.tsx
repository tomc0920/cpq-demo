import { money, percent } from "../format";
import { NumberField } from "./NumberField";
import type { Product, QuoteLine, QuoteLineInput } from "../types";

interface Props {
  lines: QuoteLineInput[];
  pricedLines: QuoteLine[];
  products: Product[];
  onChange: (index: number, patch: Partial<QuoteLineInput>) => void;
  onRemove: (index: number) => void;
}

export function QuoteLinesTable({
  lines,
  pricedLines,
  products,
  onChange,
  onRemove,
}: Props) {
  if (lines.length === 0) {
    return (
      <section className="card">
        <h3>Quote lines</h3>
        <p className="empty">
          Add a product from the catalog to start building this quote.
        </p>
      </section>
    );
  }

  return (
    <section className="card">
      <h3>Quote lines</h3>
      <div className="table-scroll">
        <table className="lines">
          <thead>
            <tr>
              <th>Product</th>
              <th>Qty</th>
              <th>Term</th>
              <th>Discount</th>
              <th>Net unit</th>
              <th className="right">Net total</th>
              <th aria-label="Remove" />
            </tr>
          </thead>
          <tbody>
            {lines.map((line, index) => {
              const product = products.find(
                (candidate) => candidate.id === line.product_id,
              );
              const priced = pricedLines[index];
              const recurring = product?.charge_type === "recurring";
              return (
                <tr key={`${line.product_id}-${index}`}>
                  <td>
                    <span className="product-name">
                      {product?.name ?? line.product_id}
                    </span>
                    <span className="muted small">{product?.sku}</span>
                    {priced && Number(priced.volume_discount_percent) > 0 && (
                      <span className="tag success">
                        Volume {percent(priced.volume_discount_percent)}
                      </span>
                    )}
                  </td>
                  <td>
                    <NumberField
                      label="Quantity"
                      min={1}
                      value={line.quantity}
                      onCommit={(next) =>
                        onChange(index, { quantity: Number(next) })
                      }
                    />
                  </td>
                  <td>
                    {recurring ? (
                      <select
                        aria-label="Term"
                        value={line.term_months}
                        onChange={(event) =>
                          onChange(index, {
                            term_months: Number(event.target.value),
                          })
                        }
                      >
                        {[12, 24, 36].map((months) => (
                          <option key={months} value={months}>
                            {months} mo
                          </option>
                        ))}
                      </select>
                    ) : (
                      <span className="muted small">one-time</span>
                    )}
                  </td>
                  <td>
                    <div className="discount-input">
                      <NumberField
                        label="Discount percent"
                        min={0}
                        max={40}
                        value={line.discount_percent}
                        onCommit={(next) =>
                          onChange(index, { discount_percent: next })
                        }
                      />
                      <span className="muted">%</span>
                    </div>
                  </td>
                  <td>{priced ? money(priced.net_unit_price) : "—"}</td>
                  <td className="right">
                    {priced && (
                      <>
                        {Number(priced.list_total) !==
                          Number(priced.net_total) && (
                          <span className="struck muted small">
                            {money(priced.list_total)}
                          </span>
                        )}
                        <strong>{money(priced.net_total)}</strong>
                      </>
                    )}
                  </td>
                  <td>
                    <button
                      type="button"
                      className="link"
                      onClick={() => onRemove(index)}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
