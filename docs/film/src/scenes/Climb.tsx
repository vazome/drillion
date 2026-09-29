import { useCurrentFrame } from "remotion";
import { Level } from "@app/Level";
import { Icon } from "@ds/Icon.jsx";
import { Caption, Stage, mix, mono, rise, useSpring, useT } from "../kit";

const DAYS = [2, 4, 8, 16, 28, 60, 120];
const W = 150, GAP = 16, X0 = 227, Y0 = 390;
const GROUPS: { of: "learning" | "familiar" | "solid"; span: number }[] = [{ of: "learning", span: 2 }, { of: "familiar", span: 3 }, { of: "solid", span: 2 }];
const GRADE = "PASSED · PASS";
const REST = " · 6m40s · 2 attempts";

/** The pass, told big: the task's rung springs one step up the ladder and leaves a ghost where it was. */
export function Climb() {
  const f = useCurrentFrame();
  const move = useSpring(30, 11, 27);
  const ghost = useT(30, 10);
  const arc = useT(34, 20);
  const typed = Math.max(0, Math.floor((f - 70) * 1.4));
  return (
    <Stage>
      <Caption eyebrow="A PASS" color="var(--pass)" left={120} top={110} size={64}>Every pass spaces it further out.</Caption>
      <svg width="1600" height="900" style={{ position: "absolute", left: 0, top: 0 }}>
        <path d="M302 372 Q385 290 452 364" fill="none" stroke="var(--accent)" strokeWidth={3} strokeLinecap="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - arc} />
        <path d="M436 350 L456 367 L431 374" fill="none" stroke="var(--accent)" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" opacity={arc > 0.95 ? 1 : 0} />
      </svg>
      <div style={{ position: "absolute", left: X0, top: Y0, width: 7 * W + 6 * GAP, height: 120 }}>
        {DAYS.map((d, i) => <Cell key={d} i={i} />)}
        <span style={{ position: "absolute", left: 0, top: 0, width: W, height: 120, boxSizing: "border-box", border: "2px dashed var(--accent-line)", borderRadius: 12, opacity: ghost }} />
        <span style={{ position: "absolute", left: mix(move, 0, W + GAP), top: -6, width: W, height: 120, boxSizing: "border-box", border: "2px solid var(--accent)", background: "var(--accent-tint)", borderRadius: 12 }} />
        {DAYS.map((d, i) => {
          const lit = Math.max(0, 1 - Math.abs(move - i));
          return <span key={d} style={{ position: "absolute", left: i * (W + GAP), top: 0, width: W, height: 120, display: "flex", alignItems: "center", justifyContent: "center", ...mono, fontSize: 36,
            color: lit > 0.5 ? "var(--accent)" : "var(--text-faint)", fontWeight: lit > 0.5 ? 500 : 400, transform: `translateY(${-6 * lit}px)` }}>{d}d</span>;
        })}
      </div>
      <div style={{ position: "absolute", left: X0, top: Y0 + 142, width: 7 * W + 6 * GAP, display: "grid", gridTemplateColumns: `repeat(7, ${W}px)`, columnGap: GAP }}>
        {GROUPS.map((g, i) => <Group key={g.of} of={g.of} span={g.span} at={58 + i * 6} />)}
      </div>
      <div style={{ position: "absolute", left: 0, top: 720, width: 1600, display: "flex", justifyContent: "center", alignItems: "center", gap: 16, ...mono, fontSize: 30, opacity: f >= 68 ? 1 : 0 }}>
        <span style={{ display: "flex", color: "var(--pass)", ...rise(useT(68, 10), 8) }}><Icon name="CheckmarkOutline" size={30} /></span>
        <span><span style={{ color: "var(--pass)", fontWeight: 500 }}>{GRADE.slice(0, typed)}</span><span style={{ color: "var(--text-muted)" }}>{REST.slice(0, Math.max(0, typed - GRADE.length))}</span></span>
      </div>
    </Stage>
  );
}

function Cell({ i }: { i: number }) {
  const t = useT(4 + i * 2, 14);
  return <span style={{ position: "absolute", left: i * (W + GAP), top: 0, width: W, height: 120, boxSizing: "border-box", border: "1px solid var(--border)", borderRadius: 12, ...rise(t, 14) }} />;
}

function Group({ of, span, at }: { of: "learning" | "familiar" | "solid"; span: number; at: number }) {
  const t = useT(at, 14);
  return (
    <div style={{ gridColumn: `span ${span}`, display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: t }}>
      <span style={{ alignSelf: "stretch", height: 2, borderRadius: 999, background: `var(--strength-${of})`, transform: `scaleX(${t})` }} />
      <span style={{ fontSize: 26, ...rise(t, 8) }}><Level of={of} /></span>
    </div>
  );
}
