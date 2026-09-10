import React from "react";
import s from "./ResultBanner.module.css";
export function ResultBanner({ state = "idle", headline, output, gradeLine, backIn, className, style }) {
  const cx = (extra) => [s.root, extra, className].filter(Boolean).join(" ");
  if (state === "idle") return <div data-state="idle" className={cx()} style={style}>Not run yet — <kbd>Ctrl+Enter</kbd> runs the tests.</div>;
  if (state === "running") return <div data-state="running" className={cx()} style={style} aria-live="polite">Running…</div>;
  if (state === "failed") return (
    <div data-state="failed" className={cx()} style={style} aria-live="polite">
      <div className={s.headline}>✗ {headline}</div>
      {output ? (
        <details className={s.details}>
          <summary className={s.summary}>Show full output</summary>
          <pre className={s.output}>{output}</pre>
        </details>
      ) : null}
    </div>
  );
  return (
    <div data-state="passed" className={cx()} style={style} aria-live="polite">
      <span className={s.grade}>✓ PASSED{gradeLine ? " · " + gradeLine : ""}</span>
      {backIn ? <span className={s.backIn}>back in {backIn}</span> : null}
    </div>
  );
}
