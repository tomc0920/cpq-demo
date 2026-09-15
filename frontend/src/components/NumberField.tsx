import { useState } from "react";

interface Props {
  value: string | number;
  onCommit: (value: string) => void;
  min: number;
  max?: number;
  step?: number;
  label: string;
}

function clamp(value: number, min: number, max?: number) {
  return Math.min(max ?? Number.POSITIVE_INFINITY, Math.max(min, value));
}

/** Number input that keeps intermediate typing intact and clamps the committed value. */
export function NumberField({ value, onCommit, min, max, step = 1, label }: Props) {
  const [draft, setDraft] = useState(String(value));
  const [editing, setEditing] = useState(false);
  const [lastValue, setLastValue] = useState(value);

  if (!editing && value !== lastValue) {
    setLastValue(value);
    setDraft(String(value));
  }

  const commit = (raw: string) => {
    const parsed = Number(raw);
    if (raw.trim() === "" || Number.isNaN(parsed)) return;
    const clamped = clamp(parsed, min, max);
    onCommit(step === 1 ? String(Math.round(clamped)) : String(clamped));
  };

  return (
    <input
      type="number"
      min={min}
      max={max}
      step={step}
      aria-label={label}
      value={draft}
      onFocus={() => setEditing(true)}
      onChange={(event) => {
        setDraft(event.target.value);
        commit(event.target.value);
      }}
      onBlur={() => {
        setEditing(false);
        const parsed = Number(draft);
        const next = draft.trim() === "" || Number.isNaN(parsed) ? min : clamp(parsed, min, max);
        setDraft(String(next));
        onCommit(String(next));
      }}
    />
  );
}
