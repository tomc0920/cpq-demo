import { useState } from "react";

interface Props {
  value: string | number;
  onCommit: (value: string) => void;
  min: number;
  max?: number;
  integer?: boolean;
  label: string;
}

/** Number input that keeps intermediate typing intact and normalizes the committed value. */
export function NumberField({ value, onCommit, min, max, integer = false, label }: Props) {
  const [draft, setDraft] = useState(String(value));
  const [editing, setEditing] = useState(false);
  const [lastValue, setLastValue] = useState(value);

  if (!editing && value !== lastValue) {
    setLastValue(value);
    setDraft(String(value));
  }

  const normalize = (raw: string) => {
    const parsed = Number(raw);
    if (raw.trim() === "" || Number.isNaN(parsed)) return null;
    const clamped = Math.min(max ?? Number.POSITIVE_INFINITY, Math.max(min, parsed));
    return String(integer ? Math.round(clamped) : clamped);
  };

  return (
    <input
      type="number"
      min={min}
      max={max}
      step={integer ? 1 : "any"}
      aria-label={label}
      value={draft}
      onFocus={() => setEditing(true)}
      onChange={(event) => {
        setDraft(event.target.value);
        const next = normalize(event.target.value);
        if (next !== null) onCommit(next);
      }}
      onBlur={() => {
        setEditing(false);
        const next = normalize(draft) ?? String(min);
        setDraft(next);
        onCommit(next);
      }}
    />
  );
}
