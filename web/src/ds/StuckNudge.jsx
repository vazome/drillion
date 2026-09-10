import React from "react";
import s from "./StuckNudge.module.css";
/* StuckNudge — arrives once a task has been open a long while. Advises a hint first and
   the material second. Never blocks the editor; dismissible for good. */
function NudgeButton({ variant, onClick, disabled, children }) {
  return <button type="button" className={s.btn + " m-press"} data-variant={variant} disabled={disabled} onClick={onClick}>{children}</button>;
}
export function StuckNudge({ minutes = 30, hintsShown = 0, hintsTotal = 3, hintReady = true, onHint, onDismiss, placement = "corner", className, style }) {
  return (
    <div className={[s.root, "m-rise", className].filter(Boolean).join(" ")} role="status" data-placement={placement} style={style}>
      <div className={s.head}>
        <span className={s.eyebrow}>{minutes} minutes on this task</span>
        <button type="button" onClick={onDismiss} aria-label="Dismiss" className={s.dismiss + " m-press"}>×</button>
      </div>
      <p className={s.lead}>
        Take a hint. It opens the next step, not the answer, and the pass still counts.
      </p>
      <p className={s.sub}>
        If the problem still doesn't come apart after one, go and read the material. You will be reading with a question in hand, which is the only way it sticks.
      </p>
      <div className={s.actions}>
        <NudgeButton onClick={onHint} disabled={!hintReady}>Show hint {hintsShown + 1}</NudgeButton>
        <div className={s.spacer}></div>
        <span className={s.count}>{hintsShown} of {hintsTotal} shown</span>
      </div>
    </div>
  );
}
