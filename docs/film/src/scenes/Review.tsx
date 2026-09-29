import React from "react";
import type { ReactNode } from "react";
import { Level } from "@app/Level";
import { Button } from "@ds/Button.jsx";
import { Icon } from "@ds/Icon.jsx";
import { Caption, Stage, Window, label, mono, rise, useSpring, useT } from "../kit";
import { Spec, TaskHeader, TopBar } from "../Task";

const LEFT = 96, TOP = 216;
const SHOT = { scale: 1408 / 1159, x: 441, y: 113 };   // the review pane, edge to edge
const PANE = 323;                                     // the diff's height, so the banner sits under it
const mark = (t: ReactNode) => <span style={{ background: "var(--accent-line)", borderRadius: 2 }}>{t}</span>;
const k = (t: string) => <span style={{ color: "var(--syn-keyword)" }}>{t}</span>;
const s = (t: ReactNode) => <span style={{ color: "var(--syn-string)" }}>{t}</span>;
const hint = (t: string) => <span style={{ color: "var(--text-faint)" }}>{t}</span>;

/** Yours and the reference, as the diff marks them: a line, and the words that differ. */
const YOURS: ReactNode[] = [
  <>{k("def")} solve(rows{mark(": list[tuple[str, float]]")}){hint(" -> str")}:</>,
  <>    {mark(<>lines{hint(": list[str]")} = [</>)}{s(<>f"{"{"}{mark("n")}:&lt;14{"}{"}{mark("v")}:&gt;12,.2f{"}"}"</>)} {k("for")} {mark("n, v")} {k("in")}</>,
  <>    {mark("rows]")}</>,
  <>    {k("return")} {s('"\\n"')}.join({mark("lines")})</>,
];
const REFERENCE: ReactNode[] = [
  <>{k("def")} solve(rows){hint(" -> str")}:</>,
  <>    {mark(<>{k("return")} {s('"\\n"')}.join(</>)}{s(<>f"{"{"}{mark("name")}:&lt;14{"}{"}{mark("value")}:&gt;12,.2f{"}"}"</>)} {k("for")} {mark("name,")}</>,
  <>    {mark("value")} {k("in")} rows{mark(")")}</>,
];

export function Review() {
  const enter = useSpring(0, 200, 16);
  return (
    <Stage>
      <Caption eyebrow="SOLVED" color="var(--pass)">Yours, beside the reference.</Caption>
      <Window left={LEFT} top={TOP} width={1408} height={740} shot={SHOT} enter={enter}>
        <TopBar />
        <TaskHeader timer="6:40" done height={65} />
        <Spec width={440} top={113} from={0} />
        <div style={{ position: "absolute", left: 441, top: 113, width: 1159, height: 52, boxSizing: "border-box", padding: "0 20px", display: "flex", alignItems: "center", gap: 16, borderBottom: "1px solid var(--border)", background: "var(--bg)" }}>
          <span style={label}>Review</span>
          <Segment items={["Compare", "Yours", "Reference"]} on={0} />
          <span style={{ color: "var(--text-muted)" }}>3 lines differ</span>
          <span style={{ flexGrow: 1 }} />
          <Segment items={["Side by side", "Inline"]} on={0} />
        </div>
        <div style={{ position: "absolute", left: 441, top: 165, width: 1159, height: PANE, background: "var(--editor)", ...mono, fontSize: 14, lineHeight: "19px" }}>
          <Side />
        </div>
        <Passed />
      </Window>
    </Stage>
  );
}

function Segment({ items, on }: { items: string[]; on: number }) {
  return (
    <div style={{ display: "flex", padding: 3, gap: 2, background: "var(--surface-2)", borderRadius: 6 }}>
      {items.map((t, i) => <span key={t} style={{ padding: "4px 14px", borderRadius: 4, background: i === on ? "var(--accent-tint)" : undefined, color: i === on ? "var(--accent)" : "var(--text-muted)" }}>{t}</span>)}
    </div>
  );
}

/** A diff line: its gutter, then the code on the tint, which washes in from `at`. */
function Row({ n, sign, at, children }: { n: string; sign: string; at: number; children: ReactNode }) {
  const t = useT(at, 12);
  return (
    <div style={{ display: "flex", whiteSpace: "pre", background: `color-mix(in srgb, var(--accent-tint) ${Math.round(t * 100)}%, transparent)` }}>
      <span style={{ width: 56, textAlign: "right", color: "var(--text-faint)" }}>{n}{sign}</span> <span>{children}</span>
    </div>
  );
}

function Side() {
  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", height: 34, alignItems: "center", borderBottom: "1px solid var(--border)", background: "var(--bg)", fontFamily: "var(--font-sans)", fontSize: 13, fontWeight: 600 }}>
        <span style={{ paddingLeft: 16, borderRight: "1px solid var(--border)" }}>Yours</span>
        <span style={{ paddingLeft: 16 }}>Reference</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", height: PANE - 34 }}>
        <div style={{ paddingTop: 4, borderRight: "2px solid var(--border)" }}>
          {YOURS.map((l, i) => <Row key={i} n={i === 2 ? "" : String(i < 2 ? i + 1 : 3)} sign="−" at={16 + i * 3}>{l}</Row>)}
        </div>
        <div style={{ paddingTop: 4 }}>
          {REFERENCE.map((l, i) => <Row key={i} n={i === 2 ? "" : String(i + 1)} sign="+" at={18 + i * 3}>{l}</Row>)}
        </div>
      </div>
    </>
  );
}

/** The pass banner under the diff: the grade line, the word, and the rung the task now sits on. */
function Passed() {
  const up = useT(30, 16);
  return (
    <div style={{ position: "absolute", left: 441, top: 165 + PANE, width: 1159, height: 188, boxSizing: "border-box", padding: "22px 24px 18px", display: "flex", flexDirection: "column", gap: 12,
      borderTop: "3px solid var(--pass)", background: "var(--bg)", ...rise(up, 24) }}>
      <span style={{ ...mono, fontSize: 15 }}><span style={{ color: "var(--pass)" }}>PASSED · PASS</span><span style={{ color: "var(--text-muted)" }}> · 6m40s · 2 attempts</span></span>
      <span style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <Level of="learning" />
        <span style={{ color: "var(--text-muted)" }}>It comes back later than last time.</span>
      </span>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 6 }}>
        {[2, 4, 8, 16, 28, 60, 120].map((d) => (
          <span key={d} style={{ width: 72, height: 28, boxSizing: "border-box", display: "flex", alignItems: "center", justifyContent: "center", borderRadius: 6, ...mono, fontSize: 13,
            ...(d === 4 ? { border: "1px solid var(--accent)", background: "var(--accent-tint)", color: "var(--accent)", fontWeight: 500 } : { background: "var(--surface-2)", color: "var(--text-faint)" }) }}>{d}d</span>
        ))}
        <span style={{ flexGrow: 1 }} />
        <Button variant="quiet">Back to Today</Button>
        <Button variant="primary">Next in Today <Icon name="ArrowRight" /></Button>
      </div>
    </div>
  );
}
