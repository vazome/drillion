import React from "react";
import s from "./FailedCase.module.css";

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
            <div className={s.value} data-wrong="">{found.actual}</div>
          </div>
          <div className={s.field}>
            <span className={s.label}>Expected</span>
            <div className={s.value} data-right="">{found.expected}</div>
          </div>
        </div>
      ) : null}
      {found.source ? <div className={s.line}>{found.source}</div> : null}
    </div>
  );
}
