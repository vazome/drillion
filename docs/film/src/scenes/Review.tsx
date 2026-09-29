import React from "react";
import type { ReactNode } from "react";
import { useCurrentFrame } from "remotion";
import { Level } from "@app/Level";
import { Button } from "@ds/Button.jsx";
import { Icon } from "@ds/Icon.jsx";
import { Caption, Cursor, Stage, Window, label, mix, mono, toFrame, useShot, useSpring, useT } from "../kit";
import { Spec, TaskHeader, TopBar } from "../Task";

const LEFT = 112, TOP = 116;
const INLINE = 104, BACK = 138;   // the two clicks on the layout switch
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
  const f = useCurrentFrame();
  const enter = useSpring(0, 200, 20);
  const shot = useShot({ scale: 0.86, x: 0, y: 0 }, { scale: 0.88, x: 24, y: 0 }, 20, 120);
  const inline = f >= INLINE && f < BACK;
  const swap = useT(INLINE, 8) - useT(BACK, 8);   // how far the pane is into Inline
  const bInline = toFrame(shot, LEFT, TOP, 1549, 139);
  const bSide = toFrame(shot, LEFT, TOP, 1468, 139);
  const go = useT(78, 22), back = useT(118, 16), off = useT(146, 14);
  const cursor = {
    x: mix(off, f < 118 ? mix(go, bInline.x + 60, bInline.x) : mix(back, bInline.x, bSide.x), bSide.x + 80),
    y: mix(off, f < 118 ? mix(go, bInline.y + 260, bInline.y) : bSide.y, bSide.y + 200),
  };
  return (
    <Stage>
      <Caption eyebrow="SOLVED" color="var(--pass)" inline left={112} top={34} size={44}>Yours, beside the reference.</Caption>
      <Window left={LEFT} top={TOP} width={1376} height={774} shot={shot} enter={enter} tilt={0}>
        <TopBar />
        <TaskHeader timer="6:40" done height={65} />
        <Spec width={440} top={113} from={0}>
          <div style={{ position: "absolute", left: 0, bottom: 0, width: 439, boxSizing: "border-box", padding: "14px 24px", display: "flex", gap: 10, alignItems: "flex-start", borderTop: "1px solid var(--border)", background: "var(--bg)", fontSize: 13, lineHeight: 1.5, color: "var(--text-muted)" }}>
            <span style={{ display: "flex", paddingTop: 2 }}><Icon name="Unlocked" size={14} /></span>
            <span>Solution open: you passed this one. It closes again when the task comes back.</span>
          </div>
        </Spec>
        <div style={{ position: "absolute", left: 441, top: 113, width: 1159, height: 52, boxSizing: "border-box", padding: "0 20px", display: "flex", alignItems: "center", gap: 16, borderBottom: "1px solid var(--border)", background: "var(--bg)" }}>
          <span style={label}>Review</span>
          <Segment items={["Compare", "Yours", "Reference"]} on={0} />
          <span style={{ color: "var(--text-muted)" }}>3 lines differ</span>
          <span style={{ flexGrow: 1 }} />
          <Segment items={["Side by side", "Inline"]} on={inline ? 1 : 0} />
        </div>
        <div style={{ position: "absolute", left: 441, top: 165, width: 1159, height: 547, background: "var(--editor)", ...mono, fontSize: 14, lineHeight: "19px" }}>
          <div style={{ position: "absolute", inset: 0, opacity: 1 - swap }}><Side /></div>
          <div style={{ position: "absolute", inset: 0, opacity: swap }}><Inline /></div>
        </div>
        <Passed />
      </Window>
      <Cursor x={cursor.x} y={cursor.y} clicks={[INLINE, BACK]} opacity={f < 78 ? 0 : 1 - off} />
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
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", height: 513 }}>
        <div style={{ paddingTop: 4, borderRight: "2px solid var(--border)" }}>
          {YOURS.map((l, i) => <Row key={i} n={i === 2 ? "" : String(i < 2 ? i + 1 : 3)} sign="−" at={6 + i * 3}>{l}</Row>)}
        </div>
        <div style={{ paddingTop: 4 }}>
          {REFERENCE.map((l, i) => <Row key={i} n={i === 2 ? "" : String(i + 1)} sign="+" at={8 + i * 3}>{l}</Row>)}
        </div>
      </div>
    </>
  );
}

function Inline() {
  return (
    <div style={{ paddingTop: 8 }}>
      {YOURS.map((l, i) => <Row key={`y${i}`} n={i === 2 ? "" : String(i < 2 ? i + 1 : 3)} sign="−" at={0}>{l}</Row>)}
      {REFERENCE.map((l, i) => <Row key={`r${i}`} n={i === 2 ? "" : String(i + 1)} sign="+" at={0}>{l}</Row>)}
    </div>
  );
}

/** The pass banner under the diff: the grade line, the rung sliding up the ladder, the word. */
function Passed() {
  const up = useT(10, 16);
  const climb = useSpring(34, 11, 27);
  const word = useT(62, 9);
  const step = word < 0.62 ? mix(word / 0.62, 0.86, 1.08) : mix((word - 0.62) / 0.38, 1.08, 1);
  return (
    <div style={{ position: "absolute", left: 441, top: 712, width: 1159, height: 188, boxSizing: "border-box", padding: "22px 24px 18px", display: "flex", flexDirection: "column", gap: 12,
      borderTop: "3px solid var(--pass)", background: "var(--bg)", opacity: up, transform: `translateY(${(1 - up) * 30}px)` }}>
      <span style={{ ...mono, fontSize: 15 }}><span style={{ color: "var(--pass)" }}>PASSED · PASS</span><span style={{ color: "var(--text-muted)" }}> · 6m40s · 2 attempts</span></span>
      <span style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ display: "inline-flex", opacity: mix(word, 0.25, 1), transform: `scale(${step})`, transformOrigin: "left center" }}><Level of="learning" /></span>
        <span style={{ color: "var(--text-muted)" }}>It comes back later than last time.</span>
      </span>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 6 }}>
        <div style={{ position: "relative", width: 7 * 78 - 6, height: 28 }}>
          {[0, 1, 2, 3, 4, 5, 6].map((i) => <span key={i} style={{ position: "absolute", left: i * 78, top: 0, width: 72, height: 28, borderRadius: 6, background: "var(--surface-2)" }} />)}
          <span style={{ position: "absolute", left: mix(climb, 0, 78), top: 0, width: 72, height: 28, boxSizing: "border-box", border: "1px solid var(--accent)", background: "var(--accent-tint)", borderRadius: 6 }} />
          {[2, 4, 8, 16, 28, 60, 120].map((d, i) => {
            const lit = Math.max(0, 1 - Math.abs(mix(climb, 0, 1) - i));
            return <span key={d} style={{ position: "absolute", left: i * 78, top: 0, width: 72, height: 28, display: "flex", alignItems: "center", justifyContent: "center", ...mono, fontSize: 13,
              color: lit > 0.5 ? "var(--accent)" : "var(--text-faint)", fontWeight: lit > 0.5 ? 500 : 400 }}>{d}d</span>;
          })}
        </div>
        <span style={{ flexGrow: 1 }} />
        <Button variant="quiet">Back to Today</Button>
        <Button variant="primary">Next in Today <Icon name="ArrowRight" /></Button>
      </div>
    </div>
  );
}
