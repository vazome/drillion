import React from "react";
const MARK = { passed: "✓", blocked: "▲", neutral: "" };
const numR = (n) => String(n).padStart(3, "0");
export function RequiresTag({ topic, title, state = "neutral", href, onClick, onPointerEnter, style }) {
  const [hover, setHover] = React.useState(false);
  const tone = state === "passed" ? { border: "var(--pass)", bg: "var(--pass-bg)", ink: "var(--pass)" }
    : state === "blocked" ? { border: "var(--warn)", bg: "var(--warn-bg)", ink: "var(--warn)" }
    : { border: "var(--border)", bg: "var(--surface-2)", ink: "var(--text-muted)" };
  const s = { display: "inline-flex", alignItems: "center", gap: "5px", fontSize: "12px", lineHeight: 1.4, padding: "2px 8px 2px 7px", borderRadius: "var(--radius-pill)", whiteSpace: "nowrap", textDecoration: "none", fontFamily: "var(--font-sans)",
    background: tone.bg, border: "1px solid " + (hover && (href || onClick) ? "var(--accent-line)" : tone.border), color: tone.ink,
    cursor: href || onClick ? "pointer" : "default", transition: "border-color var(--dur-press) var(--ease-out)", ...style };
  const why = state === "passed" ? "passed — you have this one" : state === "blocked" ? "not passed yet — this is what is blocking" : "";
  const body = (
    <React.Fragment>
      {MARK[state] ? <span aria-hidden="true" style={{ fontSize: "11px", lineHeight: 1 }}>{MARK[state]}</span> : null}
      <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: "11.5px", fontVariantNumeric: "tabular-nums", color: tone.ink }}>{numR(topic)}</span>
      {title ? <span>{title}</span> : null}
    </React.Fragment>
  );
  const shared = { style: s, title: [numR(topic) + (title ? " " + title : ""), why].filter(Boolean).join(" — "), onMouseEnter: () => setHover(true), onMouseLeave: () => setHover(false), onPointerEnter, onFocus: onPointerEnter };
  if (onClick && !href) return <button type="button" onClick={onClick} {...shared}>{body}</button>;
  return <a href={href || "#"} onClick={onClick} {...shared}>{body}</a>;
}
