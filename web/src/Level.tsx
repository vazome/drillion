import type { Strength } from "./strength";
import s from "./Level.module.css";

type Of = "easy" | "medium" | "hard" | Strength;
const BARS: Record<Of, number> = { easy: 1, medium: 2, hard: 3, learning: 1, familiar: 2, solid: 3 };

/** A difficulty or a strength as its word beside a 1–3 bar mark. Difficulty is grey; a
 *  strength wears its own colour, and never without the word and the bars. */
export function Level({ of, count }: { of: Of; count?: number }) {
  return (
    <span className={s.root} data-of={of}>
      <span aria-hidden="true" className={s.bars}>
        {[1, 2, 3].map((i) => <span key={i} data-on={i <= BARS[of] || undefined} />)}
      </span>
      {of}
      {count === undefined ? null : <span className={s.count}>{count}</span>}
    </span>
  );
}
