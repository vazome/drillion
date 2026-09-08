/** How well you know a task, in words people already use.
 *
 * The scheduler counts Leitner boxes and always will — see `docs/adr/0001-leitner-not-fsrs.md`.
 * Nobody outside spaced-repetition hobbyism has met that vocabulary, so it stops at the API
 * boundary: every screen reads a task's standing off how far out its next sighting sits. */

export type Strength = "learning" | "familiar" | "solid";

/** `box` is the scheduler's 0-based rung; `seen` is false for a task never attempted. */
export function strength(box: number, seen: boolean, ladder: number[]): Strength | null {
  if (!seen) return null;
  const days = ladder[Math.min(box, ladder.length - 1)] ?? 0;
  return days <= 4 ? "learning" : days <= 28 ? "familiar" : "solid";
}

/** Fold the scheduler's per-box counts into the three words the screens show. */
export function tally(boxes: number[], ladder: number[]) {
  const out: Record<Strength, number> = { learning: 0, familiar: 0, solid: 0 };
  boxes.forEach((n, i) => { out[strength(i, true, ladder)!] += n; });
  return out;
}

/** "3 days" / "2 weeks" / "4 months" — the length of a gap, in the unit that reads best. */
export function span(days: number) {
  if (days < 14) return `${days} days`;
  if (days < 60) return `${Math.round(days / 7)} weeks`;
  return `${Math.round(days / 30)} months`;
}

/** When something next comes round, as a person would say it. */
export function inDays(days: number) {
  if (days <= 0) return "today";
  if (days === 1) return "tomorrow";
  return `in ${span(days)}`;
}

/** The span each word covers, read off the live ladder — never a hardcoded "8 to 28 days". */
export function bands(ladder: number[]) {
  const out = {} as Record<Strength, number[]>;
  ladder.forEach((d, i) => { (out[strength(i, true, ladder)!] ??= []).push(d); });
  const phrase = (k: Strength) => {
    const d = out[k] ?? [];
    const lo = d[0], hi = d[d.length - 1];
    if (lo === hi) return `back ${inDays(lo)}`;
    // "in 2 to 4 days", not "in 2 days to 4 days", when both ends land in the same unit
    const [loN, loUnit] = span(lo).split(" ");
    const short = span(hi).endsWith(loUnit) ? loN : span(lo);
    return `back in ${short} to ${span(hi)}`;
  };
  return { learning: phrase("learning"), familiar: phrase("familiar"), solid: phrase("solid") };
}
