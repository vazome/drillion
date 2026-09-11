import React from "react";
import s from "./FailedCase.module.css";

/** A value with its own lines numbered, so a line too long for the box wraps under a blank
 *  gutter and cannot be mistaken for two. The numbers are the component's, not the grader's:
 *  hidden from a screen reader, and left out of a selection so copying gives the value back. */
function Lines({ text, side }) {
  return (
    <div className={`${s.value} ${s.lines}`} {...{ [`data-${side}`]: "" }}>
      {String(text).split("\n").map((line, i) => (
        <React.Fragment key={i}>
          <span className={s.no} aria-hidden="true">{i + 1}</span>
          <span className={s.ln}>{line}</span>
        </React.Fragment>
      ))}
    </div>
  );
}

/** The case that failed, as the grader saw it: what `solve()` was called with, what it
 *  answered, and what the answer should have been. A fresh seed builds a different case every
 *  sitting, so without the input none of the rest can be reasoned about. A run that raised
 *  has no two sides to compare and shows the input and the line alone. */
export function FailedCase({ case: found }) {
  if (!found) return null;
  const args = Object.entries(found.args ?? {});
  const compared = found.expected != null && found.actual != null;
  return (
    <div className={s.root}>
      {args.length ? (
        <div className={s.field}>
          <span className={s.label}>Input</span>
          <div className={s.value}>
            {args.map(([name, value]) => (
              <span key={name} className={s.arg}>
                <span className={s.argName}>{name} = </span>{value}
              </span>
            ))}
          </div>
        </div>
      ) : null}
      {compared ? (
        <div className={s.pair}>
          <div className={s.field}>
            <span className={s.label}>Your output</span>
            <Lines text={found.actual} side="wrong" />
          </div>
          <div className={s.field}>
            <span className={s.label}>Expected</span>
            <Lines text={found.expected} side="right" />
          </div>
        </div>
      ) : null}
      {found.source ? <div className={s.line}>{found.source}</div> : null}
    </div>
  );
}
