import React from "react";
/* Topic depth — one strip per tag: box distribution as a stacked bar, lapses, due7, seen/total. */
const STRIP_MONO = { fontFamily: "var(--font-mono)", fontVariantNumeric: "tabular-nums" };
const STRIP_LABEL = { fontSize: 11, fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--text-muted)" };
const STRIP_GRID = { display: "grid", gridTemplateColumns: "156px minmax(0, 1fr) 52px 44px 66px", gap: 12, alignItems: "center" };
const STRIP_RAMP = [16, 30, 44, 58, 72, 86, 100].map((p) => "color-mix(in srgb, var(--accent) " + p + "%, var(--surface-2))");
const STRIP_SORTS = {
  "stuck first": (a, b) => (b.boxes[0] + b.boxes[1]) / Math.max(1, b.seen) - (a.boxes[0] + a.boxes[1]) / Math.max(1, a.seen) || b.seen - a.seen,
  "neglected first": (a, b) => (b.total - b.seen) - (a.total - a.seen),
  "most lapses": (a, b) => b.lapses - a.lapses,
  "a–z": (a, b) => a.tag.localeCompare(b.tag),
};

function TopicStripsSort({ value, onChange }) {
  return (
    <div style={{ display: "flex", gap: 6 }}>
      {Object.keys(STRIP_SORTS).map((k) => (
        <button key={k} onClick={() => onChange(k)} style={{ font: "inherit", fontSize: 12, padding: "3px 9px", cursor: "pointer", whiteSpace: "nowrap", borderRadius: "var(--radius-sm)", border: "1px solid " + (k === value ? "var(--accent-line)" : "var(--border)"), background: k === value ? "var(--accent-tint)" : "var(--surface)", color: k === value ? "var(--accent)" : "var(--text-muted)" }}>{k}</button>
      ))}
    </div>
  );
}

export function TopicStrips({ tags = [], boxes = 7, defaultSort = "stuck first", maxHeight = 520, style }) {
  const [sort, setSort] = React.useState(defaultSort);
  const rows = [...tags].sort(STRIP_SORTS[sort]);
  const widest = Math.max(1, ...tags.map((t) => t.total));
  return (
    <div style={style}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <span style={{ fontSize: 13, color: "var(--text-muted)" }}>One strip per topic: its tasks spread across the ladder, pale on the left, deep on the right.</span>
        <div style={{ flex: 1 }} /><TopicStripsSort value={sort} onChange={setSort} />
      </div>
      <div style={{ ...STRIP_GRID, paddingBottom: 6, paddingRight: 10, borderBottom: "1px solid var(--border)" }}>
        <div style={STRIP_LABEL}>Tag</div><div style={STRIP_LABEL}>Ladder spread</div>
        <div style={{ ...STRIP_LABEL, textAlign: "right" }}>Lapses</div>
        <div style={{ ...STRIP_LABEL, textAlign: "right" }}>Due 7</div>
        <div style={{ ...STRIP_LABEL, textAlign: "right" }}>Seen</div>
      </div>
      <div role="table" aria-label="Ladder spread per topic" style={{ maxHeight, overflow: "auto", marginTop: 4, paddingRight: 10 }}>
        {rows.map((t) => (
          <div key={t.tag} style={{ ...STRIP_GRID, height: 26 }}>
            <a href={"#/?tag=" + encodeURIComponent(t.tag)} title={t.tag} style={{ fontSize: 13, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{t.tag}</a>
            <div style={{ display: "flex", gap: 1, width: (t.total / widest) * 100 + "%", minWidth: 8 }}
              title={t.tag + " — " + t.boxes.map((n, i) => "box " + (i + 1) + ": " + n).join(", ") + ", unseen: " + (t.total - t.seen)}>
              {t.boxes.map((n, i) => (n ? <div key={i} style={{ flex: n, height: 10, borderRadius: 1, background: STRIP_RAMP[i] }} /> : null))}
              {t.total - t.seen > 0 ? <div style={{ flex: t.total - t.seen, height: 10, borderRadius: 1, background: "var(--surface-2)", boxShadow: "inset 0 0 0 1px var(--border)" }} /> : null}
            </div>
            <div style={{ ...STRIP_MONO, fontSize: 12, textAlign: "right", color: t.lapses ? "var(--warn)" : "var(--text-faint)" }}>{t.lapses || "—"}</div>
            <div style={{ ...STRIP_MONO, fontSize: 12, textAlign: "right", color: "var(--text-muted)" }}>{t.due7}</div>
            <div style={{ ...STRIP_MONO, fontSize: 12, textAlign: "right" }}>{t.seen}<span style={{ color: "var(--text-faint)" }}>/{t.total}</span></div>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 12 }}>
        <span style={{ fontSize: 12.5, color: "var(--text-faint)" }}>{tags.length} tags · strip width is the topic's size, segments are boxes 1–{boxes} then unseen</span>
        <div style={{ flex: 1 }} />
        <div style={{ display: "flex", gap: 2, alignItems: "center" }}>
          {STRIP_RAMP.map((c, i) => <div key={i} style={{ width: 12, height: 10, borderRadius: 1, background: c }} title={"box " + (i + 1)} />)}
          <div style={{ width: 12, height: 10, borderRadius: 1, background: "var(--surface-2)", boxShadow: "inset 0 0 0 1px var(--border)", marginLeft: 3 }} title="unseen" />
        </div>
        <span style={{ fontSize: 11, color: "var(--text-faint)" }}>box 1 → 7 → unseen</span>
      </div>
    </div>
  );
}
