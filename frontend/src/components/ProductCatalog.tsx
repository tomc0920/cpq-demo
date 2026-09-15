import { useMemo, useState } from "react";

import { money, percent } from "../format";
import type { Product } from "../types";

interface Props {
  products: Product[];
  onAdd: (product: Product) => void;
  addedProductIds: string[];
}

export function ProductCatalog({ products, onAdd, addedProductIds }: Props) {
  const [search, setSearch] = useState("");

  const visible = useMemo(() => {
    const needle = search.trim().toLowerCase();
    if (!needle) return products;
    return products.filter((product) =>
      [product.name, product.sku, product.family].some((field) =>
        field.toLowerCase().includes(needle),
      ),
    );
  }, [products, search]);

  return (
    <section className="card">
      <div className="card-header">
        <h3>Product catalog</h3>
        <input
          className="search small-search"
          type="search"
          placeholder="Filter products"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>
      <div className="product-grid">
        {visible.map((product) => {
          const added = addedProductIds.includes(product.id);
          const bestTier = product.volume_tiers.at(-1);
          return (
            <article key={product.id} className="product">
              <header>
                <span className="product-name">{product.name}</span>
                <span className="tag">{product.family}</span>
              </header>
              <p className="muted small">{product.description}</p>
              <div className="product-footer">
                <span>
                  <strong>{money(product.list_price)}</strong>
                  <span className="muted small">
                    {product.charge_type === "recurring" ? " / unit / month" : " one-time"}
                  </span>
                </span>
                <button type="button" onClick={() => onAdd(product)}>
                  {added ? "Add again" : "Add"}
                </button>
              </div>
              {bestTier && (
                <span className="muted small">
                  Up to {percent(bestTier.discount_percent)} off at {bestTier.min_quantity}+ units
                </span>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
