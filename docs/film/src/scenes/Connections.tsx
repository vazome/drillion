import type { ReactNode } from "react";
import { Icon } from "@ds/Icon.jsx";
import { Caption, Stage, Window, label, mix, mono, useSpring, useT } from "../kit";

const OPENS: [string, string, string, string][] = [
  ["285", "a ConfigMap from a map: range, and why every value gets quote", "medium · new", "270"],
  ["286", "blocks from values: toYaml, nindent, and a with that renders nothing", "hard · new", "281"],
  ["287", "an optional Service: if around a whole file, and default for a value", "medium · new", "272"],
  ["288", "a Secret from values: pipelines, b64enc and quote", "medium · new", "271"],
];
const PITCH = 125.6;
const MID = 241 + (3 * PITCH + 108) / 2;   // the Opens column's centre, which the other two sit on
const NEEDS = [MID - 116.5, MID + 8.5];    // two cards, 108 tall, 125 apart
const HERE = { x: 783, y: MID - 80.5, w: 320, h: 161 };
const OUT = HERE.x + HERE.w, OPENS_X = 1184;

/** 284's lineage: what it needs, what it opens, joined by wires that draw left to right. */
export function Connections() {
  const enter = useSpring(0, 200, 16);
  const shot = { scale: 1.2, x: 360, y: 180 };
  const needs = useT(26, 16);
  const opens = useT(38, 26);
  return (
    <Stage>
      <Caption eyebrow="CONNECTIONS">Every task knows what it builds on.</Caption>
      <Window left={96} top={216} width={1408} height={740} shot={shot} appHeight={1100} enter={enter}>
        <div style={{ position: "absolute", left: 334, top: 174, width: 1250, height: 900, boxSizing: "border-box", border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface)" }} />
        {[["Needs · 2", 424], ["This task", HERE.x], ["Opens · 6", OPENS_X]].map(([t, x]) => <span key={t} style={{ ...label, position: "absolute", left: x as number, top: 205 }}>{t}</span>)}
        <svg width="1600" height="1100" style={{ position: "absolute", left: 0, top: 0, clipPath: `inset(0 ${mix(needs, 1600 - 704, 1600 - HERE.x)}px 0 0)` }}>
          <path d={`M704 ${NEEDS[0] + 54} C744 ${NEEDS[0] + 54} 743 ${MID - 13} ${HERE.x} ${MID - 13}`} fill="none" stroke="var(--pass)" strokeWidth={1.6} />
          <path d={`M704 ${NEEDS[1] + 54} C744 ${NEEDS[1] + 54} 743 ${MID + 13} ${HERE.x} ${MID + 13}`} fill="none" stroke="var(--warn)" strokeWidth={1.6} strokeDasharray="4 4" />
        </svg>
        <svg width="1600" height="1100" style={{ position: "absolute", left: 0, top: 0, clipPath: `inset(0 ${mix(opens, 1600 - OUT, 1600 - OPENS_X)}px 0 0)` }}>
          {OPENS.map((_, i) => {
            const y1 = MID - 39 + i * 26, y2 = 295 + i * PITCH;
            return <path key={i} d={`M${OUT} ${y1} C${OUT + 40} ${y1} ${OPENS_X - 40} ${y2} ${OPENS_X} ${y2}`} fill="none" stroke="var(--text-faint)" strokeWidth={1.2} strokeDasharray="4 4" opacity={0.8} />;
          })}
        </svg>
        <Card at={8} x={424} y={NEEDS[0]} n="268" flag={<span style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--pass)" }}><Icon name="Checkmark" size={12} />passed</span>} title="your first Deployment, and the two labels that have to agree" meta="easy · done" />
        <Card at={12} x={424} y={NEEDS[1]} n="279" flag={<span style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--warn)" }}><Icon name="Pending" size={12} />not passed yet</span>} title="install a chart with your own values.yaml" meta="easy · new" />
        <Card at={16} x={HERE.x} y={HERE.y} w={HERE.w} h={HERE.h} here n="284 · this task" title="your first template: the Deployment you wrote" meta="medium · new" path="helm/templates · deployment · labels" />
        {OPENS.map(([n, title, meta, also], i) => (
          <Card key={n} at={24 + i * 5} x={OPENS_X} y={241 + i * PITCH} n={n} title={title} meta={meta} also={also} />
        ))}
      </Window>
    </Stage>
  );
}

function Card({ at, x, y, w = 280, h = 108, n, flag, title, meta, also, path, here = false }: {
  at: number; x: number; y: number; w?: number; h?: number; n: string; flag?: ReactNode; title: string; meta: string; also?: string; path?: string; here?: boolean;
}) {
  const t = useSpring(at, 200, 16);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, boxSizing: "border-box", padding: here ? "18px 20px" : "14px 16px", display: "flex", flexDirection: "column", gap: here ? 10 : 6,
      border: `1px solid ${here ? "var(--accent-line)" : "var(--border)"}`, borderRadius: 8, background: here ? "var(--accent-tint)" : "var(--bg)",
      opacity: Math.min(1, t * 1.5), transform: `scale(${mix(t, 0.9, 1)})` }}>
      <div style={{ display: "flex", justifyContent: "space-between", ...mono, fontSize: here ? 13 : 12.5 }}>
        <span style={{ color: here ? "var(--accent)" : "var(--text-muted)" }}>{n}</span>{flag}
      </div>
      <span style={{ fontSize: here ? 16.5 : 14.5, fontWeight: here ? 500 : 400, lineHeight: 1.35 }}>{title}</span>
      {path ? <span style={{ ...mono, fontSize: 12.5, color: "var(--text-muted)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", flexShrink: 0 }}>{path}</span> : null}
      <span style={{ fontSize: 12.5, color: "var(--text-faint)" }}>{meta}{also ? <span style={{ ...mono, color: "var(--warn)" }}>{"   also needs "}{also}</span> : null}</span>
    </div>
  );
}
