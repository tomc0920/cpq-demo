import { money, shortDate } from "../format";
import type { Opportunity } from "../types";

interface Props {
  opportunities: Opportunity[];
  selectedId: string | null;
  search: string;
  onSearch: (value: string) => void;
  onSelect: (opportunity: Opportunity) => void;
}

export function OpportunityList({ opportunities, selectedId, search, onSearch, onSelect }: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Opportunities</h2>
        <span className="pill">Salesforce</span>
      </div>
      <input
        className="search"
        type="search"
        placeholder="Search by name, account or owner"
        value={search}
        onChange={(event) => onSearch(event.target.value)}
      />
      <ul className="opportunity-list">
        {opportunities.map((opportunity) => (
          <li key={opportunity.id}>
            <button
              type="button"
              className={opportunity.id === selectedId ? "opportunity selected" : "opportunity"}
              onClick={() => onSelect(opportunity)}
            >
              <span className="opportunity-name">{opportunity.name}</span>
              <span className="muted">{opportunity.account_name}</span>
              <span className="opportunity-meta">
                <span className="stage">{opportunity.stage}</span>
                <span>{money(opportunity.amount)}</span>
              </span>
              <span className="muted small">Closes {shortDate(opportunity.close_date)}</span>
            </button>
          </li>
        ))}
        {opportunities.length === 0 && <li className="empty">No opportunities match that search.</li>}
      </ul>
    </aside>
  );
}
