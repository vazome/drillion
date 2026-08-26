import { useEffect, useState } from "react";
import { Card, EmptyState, Ladder, StatusBadge } from "./ds/index.js";
import { api, type Progress as Payload } from "./api";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)" };

/** The per-tag coverage bar: one cell per task, filled for the ones started. */
function Bar({ seen, total }: { seen: number; total: number }) {
  return (
    <div style={{ display: "flex", gap: 2, flexWrap: "wrap", maxWidth: 340 }}>
      {Array.from({ length: total }).map((_, i) => (
        <i key={i} style={{ width: 6, height: 12, borderRadius: 1, display: "block", background: i < seen ? "var(--accent)" : "var(--border)" }} />
      ))}
    </div>
  );
}

const mmss = (s: number) => `${Math.floor(s / 60)}m${String(s % 60).padStart(2, "0")}s`;

export function Progress() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api<Payload>("/progress").then(setData).catch((e) => setError(e.message)); }, []);

  if (error) return <EmptyState message={`Could not load progress: ${error}`} />;
  if (!data) return <EmptyState message="Loading…" />;

  const tags = Object.entries(data.per_tag).sort((a, b) => b[1].total - a[1].total);
  return (
    <div style={{ maxWidth: 960, margin: "0 auto", display: "grid", gap: 20 }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 20 }}>
        <span style={LABEL}>The ladder</span>
        <span className="tabular" style={{ fontSize: 13, color: "var(--text-faint)" }}>due now {data.due} · started {data.seen} / {data.total}</span>
      </div>
      <Ladder boxes={data.boxes} />

      <span style={LABEL}>By tag</span>
      <Card padding={"8px 20px"}>
        {tags.map(([tag, t]) => (
          <div key={tag} style={{ display: "flex", alignItems: "center", gap: 16, padding: "7px 0", borderBottom: "1px solid var(--border)" }}>
            <span style={{ fontSize: 14, width: 170 }}>{tag}</span>
            <Bar seen={t.seen} total={t.total} />
            <div style={{ flex: 1 }} />
            <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-muted)" }}>{t.seen} / {t.total}</span>
          </div>
        ))}
      </Card>

      <span style={LABEL}>Recent</span>
      <Card padding={"4px 20px"}>
        {data.log.length === 0
          ? <EmptyState message="No passes logged yet. The first one lands here." />
          : [...data.log].reverse().map((row, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 16, padding: "9px 0", borderBottom: i < data.log.length - 1 ? "1px solid var(--border)" : "none" }}>
                <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-faint)" }}>{row.date}</span>
                <a href={`#/task/${encodeURIComponent(row.slug)}`} style={{ fontFamily: "var(--font-mono)", fontSize: 13.5, flex: 1, color: "var(--text)" }}>{row.slug}</a>
                <StatusBadge status={row.grade.toLowerCase()} />
                <span className="tabular" style={{ fontSize: 13, color: "var(--text-muted)" }}>{row.attempts} attempts</span>
                <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-muted)", width: 64, textAlign: "right" }}>{mmss(row.secs)}</span>
              </div>
            ))}
      </Card>
    </div>
  );
}
