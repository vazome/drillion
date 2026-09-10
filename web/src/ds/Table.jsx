import React from "react";
import s from "./Table.module.css";
export function Table({ columns = [], rows = [], sortKey, sortDir = "asc", onSort, onRowClick, emptyMessage, className, style }) {
  const cellAttrs = (col) => ({ "data-align": col.align || undefined, "data-mono": col.mono ? "" : undefined, "data-numeric": col.numeric ? "" : undefined });
  return (
    <table className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <thead>
        <tr>
          {columns.map((col) => {
            const active = sortKey === col.key;
            const sortable = col.sortable && !!onSort;
            const nextDir = active && sortDir === "asc" ? "desc" : "asc";
            return (
              <th key={col.key} scope="col" className={s.th} {...cellAttrs(col)} data-sortable={sortable ? "" : undefined} data-active={active ? "" : undefined} style={{ width: col.width }}
                aria-sort={sortable ? (active ? (sortDir === "asc" ? "ascending" : "descending") : "none") : undefined}>
                {sortable ? (
                  <button type="button" className={s.sortBtn} onClick={() => onSort(col.key, nextDir)} aria-label={"Sort by " + col.label + " " + (nextDir === "asc" ? "ascending" : "descending")}>
                    <span>{col.label}</span>
                    <span aria-hidden="true" className={s.arrow} data-active={active ? "" : undefined}>{active ? (sortDir === "asc" ? "▲" : "▼") : ""}</span>
                  </button>
                ) : col.label}
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr><td colSpan={columns.length} className={s.empty}>{emptyMessage || "Nothing here."}</td></tr>
        ) : rows.map((row, i) => {
          const dim = !!row.disabled;
          const clickable = !!onRowClick && !dim;
          return (
            <tr key={row.id != null ? row.id : i} tabIndex={clickable ? 0 : undefined} className={s.row}
              data-dim={dim ? "" : undefined} data-clickable={clickable ? "" : undefined}
              onClick={clickable ? () => onRowClick(row) : undefined}
              onKeyDown={clickable ? (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onRowClick(row); } } : undefined}>
              {columns.map((col) => (
                <td key={col.key} className={s.td} {...cellAttrs(col)} data-muted={col.muted ? "" : undefined} data-small={col.small ? "" : undefined} style={{ width: col.width }}>
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
