import type { Opportunity, Product, Quote, QuoteInput, SyncResult } from "./types";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail ?? `Request failed with status ${response.status}`);
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

export const api = {
  listOpportunities: (search: string) =>
    request<Opportunity[]>(`/opportunities?search=${encodeURIComponent(search)}`),
  listProducts: () => request<Product[]>("/products"),
  listQuotes: (opportunityId: string) =>
    request<Quote[]>(`/quotes?opportunity_id=${encodeURIComponent(opportunityId)}`),
  previewQuote: (payload: QuoteInput, signal?: AbortSignal) =>
    request<Quote>("/quotes/preview", { method: "POST", body: JSON.stringify(payload), signal }),
  createQuote: (payload: QuoteInput) =>
    request<Quote>("/quotes", { method: "POST", body: JSON.stringify(payload) }),
  updateQuote: (id: string, payload: QuoteInput) =>
    request<Quote>(`/quotes/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  approveQuote: (id: string) => request<Quote>(`/quotes/${id}/approve`, { method: "POST" }),
  syncQuote: (id: string) => request<SyncResult>(`/quotes/${id}/sync`, { method: "POST" }),
};
