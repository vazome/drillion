import React from "react";
const ringTable = (e) => { try { return e.target.matches(":focus-visible"); } catch (_) { return true; } };
export function Table({ columns = [], rows = [], sortKey, sortDir = "asc", onSort, onRowClick, emptyMessage, style }) {
  const [hoverRow, setHoverRow] = React.useState(null);
  const [focusRow, setFocusRow] = React.useState(null);
  const [hoverCol, setHoverCol] = React.useState(null);
  const [focusCol, setFocusCol] = React.useState(null);
  const cell = (col) => ({ padding: "0 12px", textAlign: col.align || "left", width: col.width, whiteSpace: "nowrap", fontFamily: col.mono ? "var(--font-mono)" : "var(--font-sans)", fontVariantNumeric: (col.mono || col.numeric) ? "tabular-nums" : "normal" });
  return (
    <table style={{ width: "100%", borderCollapse: "collapse", background: "var(--surface)", fontSize: "14px", color: "var(--text)", ...style }}>
      <thead>
        <tr>
          {columns.map((col) => {
            const active = sortKey === col.key;
            const sortable = col.sortable && !!onSort;
            const arrow = active ? (sortDir === "asc" ? "▲" : "▼") : (hoverCol === col.key ? "▲" : "");
            return (
              <th key={col.key} scope="col" style={{ ...cell(col), padding: sortable ? 0 : "0 12px", height: "32px", borderBottom: "1px solid var(--border)", fontFamily: "var(--font-sans)", fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase", color: active ? "var(--text)" : "var(--text-muted)" }}>
                {sortable ? (
                  <button type="button" onClick={() => onSort(col.key, active && sortDir === "asc" ? "desc" : "asc")} aria-label={"Sort by " + col.label}
                    onMouseEnter={() => setHoverCol(col.key)} onMouseLeave={() => setHoverCol(null)}
                    onFocus={(e) => setFocusCol(ringTable(e) ? col.key : null)} onBlur={() => setFocusCol(null)}
                    style={{ width: "100%", height: "32px", display: "inline-flex", alignItems: "center", gap: "5px", justifyContent: col.align === "right" ? "flex-end" : "flex-start", padding: "0 12px", background: "transparent", border: "none", borderRadius: "var(--radius-sm)", font: "inherit", letterSpacing: "inherit", textTransform: "inherit", color: (active || hoverCol === col.key) ? "var(--text)" : "var(--text-muted)", cursor: "pointer", boxShadow: focusCol === col.key ? "var(--focus-ring)" : "none" }}>
                    <span>{col.label}</span>
                    <span aria-hidden="true" style={{ fontSize: "8px", lineHeight: 1, color: active ? "var(--accent)" : "var(--text-faint)", width: "7px" }}>{arrow}</span>
                  </button>
                ) : col.label}
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr><td colSpan={columns.length} style={{ height: "76px", textAlign: "center", color: "var(--text-muted)", borderTop: "1px solid var(--border)" }}>{emptyMessage || "Nothing here."}</td></tr>
        ) : rows.map((row, i) => {
          const dim = !!row.disabled;
          const clickable = !!onRowClick && !dim;
          return (
            <tr key={row.id != null ? row.id : i} tabIndex={clickable ? 0 : undefined}
              onClick={clickable ? () => onRowClick(row) : undefined}
              onKeyDown={clickable ? (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onRowClick(row); } } : undefined}
              onMouseEnter={() => setHoverRow(i)} onMouseLeave={() => setHoverRow(null)}
              onFocus={clickable ? (e) => setFocusRow(ringTable(e) ? i : null) : undefined} onBlur={clickable ? () => setFocusRow(null) : undefined}
              style={{ height: "40px", background: (hoverRow === i && clickable) ? "var(--surface-2)" : "transparent", color: dim ? "var(--text-faint)" : "var(--text)", cursor: clickable ? "pointer" : "default", outline: "none", boxShadow: focusRow === i ? "var(--focus-ring)" : "none" }}>
              {columns.map((col) => (
                <td key={col.key} style={{ ...cell(col), borderTop: "1px solid var(--border)", color: col.muted ? "var(--text-muted)" : "inherit", fontSize: col.small ? "12.5px" : "inherit", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {col.render ? col.render(row) : row[col.key]}
                </td>
              ))}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
