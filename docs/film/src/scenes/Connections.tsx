import type { ReactNode } from "react";
import { Icon } from "@ds/Icon.jsx";
import { Caption, Stage, Window, label, mix, mono, useShot, useSpring, useT } from "../kit";

const OPENS: [string, string, string, string][] = [
  ["285", "a ConfigMap from a map: range, and why every value gets quote", "medium · new", "270"],
  ["286", "blocks from values: toYaml, nindent, and a with that renders nothing", "hard · new", "281"],
  ["287", "an optional Service: if around a whole file, and default for a value", "medium · new", "272"],
  ["288", "a Secret from values: pipelines, b64enc and quote", "medium · new", "271"],
  ["314", "_helpers.tpl: name and label a release once, use it everywhere", "medium · new", ""],
  ["316", "required and fail: a chart that refuses to install broken", "medium · new", ""],
];
const PITCH = 125.6;

/** 284's lineage: what it needs, what it opens, joined by wires that draw left to right. */
export function Connections() {
  const enter = useSpring(0, 200, 20);
  const shot = useShot({ scale: 1.2, x: 340, y: 180 }, { scale: 1.2, x: 340, y: 330 }, 70, 70);
  const needs = useT(26, 16);
  const opens = useT(38, 26);
  return (
    <Stage>
      <Caption eyebrow="CONNECTIONS">Every task knows what it builds on.</Caption>
      <Window left={96} top={216} width={1408} height={740} shot={shot} appHeight={1100} enter={enter}>
        <div style={{ position: "absolute", left: 334, top: 174, width: 1180, height: 900, boxSizing: "border-box", border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface)" }} />
        {[["Needs · 2", 424], ["This task", 784], ["Opens · 6", 1144]].map(([t, x]) => <span key={t} style={{ ...label, position: "absolute", left: x as number, top: 205 }}>{t}</span>)}
        <svg width="1600" height="1100" style={{ position: "absolute", left: 0, top: 0, clipPath: `inset(0 ${mix(needs, 896, 817)}px 0 0)` }}>
          <path d="M704 547 C744 547 743 596 783 596" fill="none" stroke="var(--pass)" strokeWidth={1.6} />
          <path d="M704 672 C744 672 743 622 783 622" fill="none" stroke="var(--warn)" strokeWidth={1.6} strokeDasharray="4 4" />
        </svg>
        <svg width="1600" height="1100" style={{ position: "absolute", left: 0, top: 0, clipPath: `inset(0 ${mix(opens, 536, 456)}px 0 0)` }}>
          {OPENS.map((_, i) => {
            const y1 = 548 + i * 24, y2 = 295 + i * PITCH;
            return <path key={i} d={`M1064 ${y1} C1110 ${y1} 1098 ${y2} 1144 ${y2}`} fill="none" stroke="var(--text-faint)" strokeWidth={1.2} strokeDasharray="4 4" opacity={0.8} />;
          })}
        </svg>
        <Card at={8} x={424} y={493} n="268" flag={<span style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--pass)" }}><Icon name="Checkmark" size={12} />passed</span>} title="your first Deployment, and the two labels that have to agree" meta="easy · done" />
        <Card at={12} x={424} y={618} n="279" flag={<span style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--warn)" }}><Icon name="Pending" size={12} />not passed yet</span>} title="install a chart with your own values.yaml" meta="easy · new" />
        <Card at={16} x={783} y={529} h={161} here n="284 · this task" title="your first template: the Deployment you wrote, with…" meta="medium · new" path="helm/templates · deployment · labels" />
        {OPENS.map(([n, title, meta, also], i) => (
          <Card key={n} at={24 + i * 5} x={1144} y={241 + i * PITCH} n={n} title={title} meta={meta} also={also} />
        ))}
      </Window>
    </Stage>
  );
}

function Card({ at, x, y, h = 108, n, flag, title, meta, also, path, here = false }: {
  at: number; x: number; y: number; h?: number; n: string; flag?: ReactNode; title: string; meta: string; also?: string; path?: string; here?: boolean;
}) {
  const t = useSpring(at, 14, 22);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: here ? 281 : 280, height: h, boxSizing: "border-box", padding: here ? "18px 20px" : "14px 16px", display: "flex", flexDirection: "column", gap: here ? 10 : 6,
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
