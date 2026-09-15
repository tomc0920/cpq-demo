import type {
  Opportunity,
  Product,
  Quote,
  QuoteInput,
  SyncResult,
} from "./types";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

/** FastAPI returns `detail` as a string, or as a list of validation error objects. */
function errorMessage(body: unknown): string | null {
  if (typeof body !== "object" || body === null || !("detail" in body))
    return null;
  const detail = (body as { detail: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) =>
        typeof item === "object" && item !== null && "msg" in item
          ? String((item as { msg: unknown }).msg)
          : null,
      )
      .filter((msg): msg is string => Boolean(msg));
    if (messages.length > 0) return messages.join("; ");
  }
  return null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    throw new Error(
      errorMessage(body) ?? `Request failed with status ${response.status}`,
    );
  }
  return response.status === 204
    ? (undefined as T)
    : ((await response.json()) as T);
}

export const api = {
  listOpportunities: (search: string) =>
    request<Opportunity[]>(
      `/opportunities?search=${encodeURIComponent(search)}`,
    ),
  listProducts: () => request<Product[]>("/products"),
  listQuotes: (opportunityId: string) =>
    request<Quote[]>(
      `/quotes?opportunity_id=${encodeURIComponent(opportunityId)}`,
    ),
  previewQuote: (payload: QuoteInput, signal?: AbortSignal) =>
    request<Quote>("/quotes/preview", {
      method: "POST",
      body: JSON.stringify(payload),
      signal,
    }),
  createQuote: (payload: QuoteInput) =>
    request<Quote>("/quotes", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateQuote: (id: string, payload: QuoteInput) =>
    request<Quote>(`/quotes/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  approveQuote: (id: string) =>
    request<Quote>(`/quotes/${id}/approve`, { method: "POST" }),
  syncQuote: (id: string) =>
    request<SyncResult>(`/quotes/${id}/sync`, { method: "POST" }),
};
