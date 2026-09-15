const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 2,
});

export const money = (value: string | number) => currency.format(Number(value));

export const percent = (value: string | number) => `${Number(value).toFixed(1)}%`;

export const shortDate = (value: string) =>
  new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
