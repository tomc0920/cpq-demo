export type ChargeType = "one_time" | "recurring";

export interface Opportunity {
  id: string;
  name: string;
  account_id: string;
  account_name: string;
  stage: string;
  amount: string;
  close_date: string;
  owner_name: string;
}

export interface VolumeTier {
  min_quantity: number;
  discount_percent: string;
}

export interface Product {
  id: string;
  name: string;
  sku: string;
  family: string;
  description: string;
  list_price: string;
  charge_type: ChargeType;
  volume_tiers: VolumeTier[];
}

export interface QuoteLineInput {
  product_id: string;
  quantity: number;
  term_months: number;
  discount_percent: string;
}

export interface QuoteLine extends QuoteLineInput {
  id: string;
  name: string;
  sku: string;
  family: string;
  charge_type: ChargeType;
  list_price: string;
  volume_discount_percent: string;
  effective_discount_percent: string;
  net_unit_price: string;
  list_total: string;
  net_total: string;
}

export interface QuoteTotals {
  list_total: string;
  discount_total: string;
  net_total: string;
  one_time_total: string;
  recurring_total: string;
  annual_recurring_revenue: string;
  effective_discount_percent: string;
}

export interface Quote {
  id: string;
  name: string;
  opportunity_id: string;
  opportunity_name: string;
  account_name: string;
  status: "Draft" | "Needs Approval" | "Approved" | "Synced to Salesforce";
  lines: QuoteLine[];
  quote_discount_percent: string;
  totals: QuoteTotals;
  requires_approval: boolean;
  approval_reason: string | null;
  expires_on: string | null;
  created_at: string;
  updated_at: string;
  synced_at: string | null;
}

export interface QuoteInput {
  opportunity_id: string;
  name?: string;
  lines: QuoteLineInput[];
  quote_discount_percent: string;
}

export interface SyncResult {
  quote: Quote;
  opportunity: Opportunity;
}
