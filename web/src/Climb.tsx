import { useEffect, useId, useState } from "react";
import { m } from "motion/react";
import { dur } from "./motion";
import s from "./Climb.module.css";

/** In ms: how long the climb waits, so the editor has given way to Review and the move is the
 *  thing you see, and how long it takes to land. The strength word steps after both. */
export const CLIMB = { wait: 700, move: 900 };

/** The ladder in the pass banner, rungs named by their return interval. The task's rung slides
 *  from where it was to where this pass put it, on a spring: a climb overshoots a little and
 *  settles, a fall does not bounce. One rung is lit, the one it sits on; the rest are quiet. */
export function Climb({ ladder, from, to }: { ladder: number[]; from: number; to: number }) {
  const id = useId();
  const still = !dur("base");   // reduced motion: drawn where it landed
  const [at, setAt] = useState(still ? to : from);
  useEffect(() => {
    const t = setTimeout(() => setAt(to), still ? 0 : CLIMB.wait);
    return () => clearTimeout(t);
  }, [to, still]);
  const moved = from !== to;
  return (
    <div className={s.root} role="img"
      aria-label={moved ? `Moved from ${ladder[from]} days to ${ladder[to]} days.` : `Stays at ${ladder[to]} days.`}>
      {ladder.map((d, i) => (
        <span key={d} className={s.rung}>
          {i === at ? <m.span layoutId={id} className={s.here}
            transition={{ type: "spring", visualDuration: CLIMB.move / 1000, bounce: to < from ? 0 : 0.3 }} /> : null}
          <span className={s.days}>{d}d</span>
        </span>
      ))}
    </div>
  );
}
