import { staticFile } from "remotion";
import { Icon } from "@ds/Icon.jsx";
import { Wordmark, label, mono } from "./kit";

export const TRACK_LIST: [string, number][] = [
  ["All tracks", 385], ["argocd", 14], ["docker", 15], ["git", 18], ["github-actions", 15],
  ["helm", 15], ["kubernetes", 26], ["python", 267], ["sql", 15],
];
export const ROW = 51;          // one track row, highlight included
export const ROWS_TOP = 199;    // the first row's top, in app pixels

/** The app's sidebar. `at` is the lit row, fractional while the highlight slides between two. */
export function Sidebar({ at, page = "Catalogue" }: { at: number; page?: "Catalogue" | "Progress" }) {
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: 248, height: 900, boxSizing: "border-box", padding: "28px 16px 20px", borderRight: "1px solid var(--border)" }}>
      <div style={{ display: "flex", padding: "0 10px" }}><Wordmark size={20} /></div>
      {(["Catalogue", "Progress"] as const).map((p, i) => (
        <div key={p} style={{ marginTop: i ? 4 : 26, padding: "7px 10px", borderRadius: 6, background: p === page ? "var(--surface-2)" : undefined, fontWeight: p === page ? 500 : 400, color: p === page ? "var(--text)" : "var(--text-muted)" }}>{p}</div>
      ))}
      <div style={{ ...label, margin: "34px 10px 10px" }}>New picks from</div>
      <div style={{ position: "absolute", left: 16, right: 16, top: ROWS_TOP + at * ROW, height: ROW - 4, borderRadius: 6, background: "var(--accent-tint)" }} />
      {TRACK_LIST.map(([name, count], i) => {
        const lit = Math.max(0, 1 - Math.abs(at - i));
        return (
          <div key={name} style={{ position: "absolute", left: 16, right: 16, top: ROWS_TOP + i * ROW, height: ROW - 4, boxSizing: "border-box", padding: "8px 10px", display: "grid", gridTemplateColumns: "28px 1fr auto", alignItems: "center", gap: "6px 10px" }}>
            {i === 0
              ? <span style={{ gridRow: "span 2", width: 28, height: 28, display: "flex", alignItems: "center", justifyContent: "center", boxSizing: "border-box", border: "1px solid var(--border-strong)", borderRadius: 4, color: "var(--text-muted)" }}>
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.1"><rect x="1" y="1" width="5" height="5" /><rect x="8" y="1" width="5" height="5" /><rect x="1" y="8" width="5" height="5" /><rect x="8" y="8" width="5" height="5" /></svg>
                </span>
              : <img src={staticFile(`tracks/${name}.svg`)} alt="" style={{ gridRow: "span 2", width: 28, height: 28, objectFit: "contain", filter: name === "helm" ? "brightness(0) invert(1)" : undefined }} />}
            <span style={{ color: lit > 0.5 ? "var(--accent)" : "var(--text)", fontWeight: lit > 0.5 ? 600 : 500 }}>{name}</span>
            <span style={{ ...mono, fontSize: 12.5, color: "var(--text-muted)" }}>{count}</span>
            <span style={{ gridColumn: "2 / -1", justifySelf: "start", minWidth: 6, height: 3, borderRadius: 999, width: `${(100 * count) / 385}%`, background: lit > 0.5 ? "var(--accent-line)" : "var(--border)" }} />
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 16, right: 16, bottom: 20, display: "flex", flexDirection: "column" }}>
        <span style={{ height: 1, background: "var(--border)", marginBottom: 16 }} />
        <span style={{ display: "flex", alignItems: "center", gap: 10, padding: "6px 10px", color: "var(--text-muted)" }}><Icon name="Settings" />Settings</span>
        <span style={{ display: "flex", alignItems: "center", gap: 10, padding: "6px 10px", color: "var(--text-muted)" }}>
          <Icon name="Asleep" />Dark
        </span>
        <span style={{ padding: "8px 10px 0", ...mono, fontSize: 11.5, color: "var(--text-muted)" }}>v0.11.2 · Python 3.14.5</span>
      </div>
    </div>
  );
}
