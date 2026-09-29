import type { CSSProperties } from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Icon } from "@ds/Icon.jsx";
import { StatusBadge } from "@ds/StatusBadge.jsx";
import { Caption, INOUT, Stage, Window, label, mono, rise, useSpring, useT } from "../kit";

/** A year of practice, made up the way the design system's own Progress screen is: the habit
 *  thickens as the weeks go on. Seeded, so every render draws the same year. */
const YEAR = (() => {
  let seed = 7;
  const rnd = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;
  return Array.from({ length: 53 }, (_, w) => Array.from({ length: w === 52 ? 3 : 7 }, () => {
    const r1 = rnd(), r2 = rnd();
    return r1 < 0.3 + 0.5 * Math.min(1, w / 36) ? 1 + Math.floor(r2 * r2 * 4) : 0;
  }));
})();
const MONTHS: [string, number][] = [["Oct", 1], ["Nov", 5], ["Dec", 10], ["Jan", 14], ["Feb", 18], ["Mar", 22], ["Apr", 27], ["May", 31], ["Jun", 36], ["Jul", 40], ["Aug", 44], ["Sep", 49]];
const TOPICS: [string, number, number, number, number, number][] = [
  ["strings", 13, 3, 4, 2, 2], ["numbers", 11, 2, 5, 1, 1], ["sorted", 9, 2, 3, 1, 0], ["deployment", 6, 1, 2, 2, 1],
];
const LOG: [string, string, "pass" | "quick" | "struggled", number, string][] = [
  ["Sep 29", "009_fstrings", "pass", 2, "6m40s"], ["Sep 28", "284_helm_template_deployment", "quick", 1, "3m12s"],
  ["Sep 28", "331_sql_running_total", "struggled", 4, "22m05s"], ["Sep 27", "346_git_resolve_a_conflict", "pass", 1, "8m30s"],
];
const card: CSSProperties = { position: "absolute", boxSizing: "border-box", border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface)" };

export function Progress() {
  const f = useCurrentFrame();
  const enter = useSpring(0, 200, 16);
  const shot = { scale: 1.1, x: 278, y: 700 };   // the three cards, even margins, whole rows only
  const weeks = interpolate(f, [8, 56], [0, 53], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: INOUT });
  const grown = useT(46, 30);
  return (
    <Stage>
      <Caption eyebrow="PROGRESS">It fills in as you practise.</Caption>
      <Window left={96} top={216} width={1408} height={740} shot={shot} appHeight={1400} enter={enter}>
        <div style={{ ...card, left: 330, top: 722, width: 1175, height: 290, padding: "24px 26px", display: "flex", flexDirection: "column", gap: 14 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 14 }}>
            <span style={label}>Practice · last 12 months</span>
            <span style={{ color: "var(--text-muted)" }}>Passes per day. Started early October.</span>
          </div>
          <div style={{ position: "relative", height: 16, fontSize: 11, color: "var(--text-muted)" }}>
            {MONTHS.map(([m, c]) => <span key={m} style={{ position: "absolute", left: c * 21.2, top: 0 }}>{m}</span>)}
          </div>
          <div style={{ display: "flex", gap: 4.2 }}>
            {YEAR.map((days, w) => (
              <div key={w} style={{ display: "flex", flexDirection: "column", gap: 4.2 }}>
                {days.map((lvl, d) => {
                  const into = Math.max(0, Math.min(1, weeks - w - d / 7));   // how far this day's square has filled
                  const on = lvl && into > 0;
                  return <span key={d} style={{ width: 17, height: 17, borderRadius: 2, background: "var(--heat-0)", position: "relative" }}>
                    {on ? <span style={{ position: "absolute", inset: 0, borderRadius: 2, background: `var(--heat-${lvl})`, opacity: Math.min(1, into * 2), transform: `scale(${0.4 + 0.6 * Math.min(1, into * 1.6)})` }} /> : null}
                  </span>;
                })}
              </div>
            ))}
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 4, fontSize: 12, color: "var(--text-muted)" }}>
            <span style={{ marginRight: 4 }}>less</span>
            {[0, 1, 2, 3, 4].map((h) => <span key={h} style={{ width: 11, height: 11, borderRadius: 2, background: `var(--heat-${h})` }} />)}
            <span style={{ marginLeft: 4 }}>more</span>
          </div>
        </div>

        <div style={{ ...card, left: 330, top: 1036, width: 576, height: 520, padding: "24px 22px", display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <span style={label}>Topic depth</span>
            <span style={{ display: "flex", alignItems: "center", gap: 6 }}>stuck first<Icon name="ChevronDown" size={14} /></span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "120px minmax(0, 1fr) 56px 56px", columnGap: 14, alignItems: "center", height: 30, borderBottom: "1px solid var(--border)", ...label, fontSize: 11.5 }}>
            <span>Tag</span><span>Spread</span><span style={{ textAlign: "right" }}>Seen</span><span style={{ textAlign: "right" }}>Due 7d</span>
          </div>
          {TOPICS.map(([tag, total, l, fa, so, due]) => {
            const seen = Math.round((l + fa + so) * grown);
            return (
              <div key={tag} style={{ display: "grid", gridTemplateColumns: "120px minmax(0, 1fr) 56px 56px", columnGap: 14, alignItems: "center", height: 48, borderBottom: "1px solid var(--border)" }}>
                <span style={mono}>{tag}</span>
                <span style={{ display: "flex", height: 6, borderRadius: 999, overflow: "hidden", background: "var(--surface-2)" }}>
                  {([[l, "learning"], [fa, "familiar"], [so, "solid"]] as const).map(([n, of]) => <span key={of} style={{ width: `${(n / total) * 100 * grown}%`, background: `var(--strength-${of})` }} />)}
                </span>
                <span style={{ ...mono, textAlign: "right" }}>{seen}/{total}</span>
                <span style={{ ...mono, textAlign: "right" }}>{grown > 0.9 ? due : 0}</span>
              </div>
            );
          })}
        </div>

        <div style={{ ...card, left: 929, top: 1036, width: 576, height: 520, padding: "24px 22px", display: "flex", flexDirection: "column" }}>
          <span style={{ ...label, marginBottom: 14 }}>Last 30 sessions</span>
          <div style={{ display: "grid", gridTemplateColumns: "64px minmax(0, 1fr) 92px 44px 64px", columnGap: 10, alignItems: "center", height: 34, borderBottom: "1px solid var(--border)", ...label, fontSize: 11.5 }}>
            <span>Date</span><span>Task</span><span>Grade</span><span style={{ textAlign: "right" }}>Tries</span><span style={{ textAlign: "right" }}>Active</span>
          </div>
          {LOG.map((r, i) => <Session key={i} r={r} at={70 + i * 6} />)}
        </div>
      </Window>
    </Stage>
  );
}

/** One logged session, landing in reading order. */
function Session({ r: [date, slug, grade, tries, active], at }: { r: (typeof LOG)[number]; at: number }) {
  const t = useT(at, 12);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "64px minmax(0, 1fr) 92px 44px 64px", columnGap: 10, alignItems: "center", height: 40, borderBottom: "1px solid var(--border)", ...mono, fontSize: 13, ...rise(t, 8) }}>
      <span style={{ color: "var(--text-muted)" }}>{date}</span>
      <span style={{ color: "var(--accent)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{slug}</span>
      <span><StatusBadge status={grade} /></span>
      <span style={{ textAlign: "right" }}>{tries}</span>
      <span style={{ textAlign: "right", color: "var(--text-muted)" }}>{active}</span>
    </div>
  );
}
