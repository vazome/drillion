import React from "react";
import css from "./RequiresTag.module.css";
const MARK = { passed: "✓", blocked: "▲", neutral: "" };
const numR = (n) => String(n).padStart(3, "0");
export function RequiresTag({ topic, title, state = "neutral", href, onClick, onPointerEnter, className, style }) {
  const interactive = !!(href || onClick);
  const why = state === "passed" ? "passed — you have this one" : state === "blocked" ? "not passed yet — this is what is blocking" : "";
  const body = (
    <React.Fragment>
      {MARK[state] ? <span aria-hidden="true" className={css.mark}>{MARK[state]}</span> : null}
      <span className={css.num + " tabular"}>{numR(topic)}</span>
      {title ? <span>{title}</span> : null}
    </React.Fragment>
  );
  const shared = {
    className: [css.root, className].filter(Boolean).join(" "), style,
    "data-state": state, "data-interactive": interactive ? "" : undefined,
    title: [numR(topic) + (title ? " " + title : ""), why].filter(Boolean).join(" — "),
    onPointerEnter, onFocus: onPointerEnter,
  };
  if (onClick && !href) return <button type="button" onClick={onClick} {...shared}>{body}</button>;
  return <a href={href || "#"} onClick={onClick} {...shared}>{body}</a>;
}
