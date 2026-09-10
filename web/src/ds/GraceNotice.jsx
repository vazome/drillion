import React from "react";
import s from "./GraceNotice.module.css";
/* GraceNotice — the corner notice that explains why the clock still reads 00:00. Up from the
   moment a fresh attempt opens, and gone on its own when the reading grace runs out.
   Same shell as StuckNudge: this is a nudge too, just an early and quieter one.
   The eyebrow is not "Read first": every task README already owns that heading. */
export function GraceNotice({ seconds = 60, onDismiss, className, style }) {
  return (
    <div className={[s.root, "m-rise", className].filter(Boolean).join(" ")} role="status" style={style}>
      <div className={s.head}>
        <span className={s.eyebrow}>Reading time</span>
        <button type="button" onClick={onDismiss} aria-label="Dismiss" className={s.dismiss + " m-press"}>×</button>
      </div>
      <p className={s.body}>
        The clock starts in <span className={s.count + " tabular"}>{seconds}</span> {seconds === 1 ? "second" : "seconds"}. Read the whole spec before you write anything — it costs you nothing.
      </p>
    </div>
  );
}
