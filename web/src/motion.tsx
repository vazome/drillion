import { AnimatePresence, LazyMotion, MotionConfig, domMax, m } from "motion/react";
import type { CSSProperties, ReactNode } from "react";

type Dur = "press" | "fast" | "base" | "slow";
type Ease = "out" | "in" | "inout" | "step";

const read = new Map<string, string>();
/** A motion token as `ds/tokens/motion.css` defines it, so Motion and CSS keep one set of timings. */
function token(name: string) {
  if (!read.has(name)) read.set(name, getComputedStyle(document.documentElement).getPropertyValue(`--${name}`).trim());
  return read.get(name)!;
}
const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Seconds, as Motion takes them; 0 under reduced motion, the way motion.css collapses. The
 *  unit is read, not assumed: the build minifies `200ms` to `.2s`. */
export function dur(name: Dur) {
  if (reduced()) return 0;
  const v = token(`dur-${name}`);
  return parseFloat(v) / (v.endsWith("ms") ? 1000 : 1);
}
/** The token's cubic-bezier as the four numbers Motion takes. */
export const ease = (name: Ease) => token(`ease-${name}`).match(/-?[\d.]+/g)!.map(Number) as [number, number, number, number];

/** Wraps the app once: `m` elements load their features here, and honour reduced motion. */
export function Motion({ children }: { children: ReactNode }) {
  return <LazyMotion features={domMax} strict><MotionConfig reducedMotion="user">{children}</MotionConfig></LazyMotion>;
}

/* Under reduced motion both below start where they end, with no first frame at opacity 0:
   a zero duration still paints that frame once before the animation runs. */

/** Something that appears in place and goes again, like a notice: pass it as the child while
 *  it shows and `null` once it has gone, and it lifts out instead of vanishing. `y` is where it
 *  comes from (above by default); `enter={false}` when the child already animates itself in. */
export function Drop({ children, y = -7, enter = true, className, style }: {
  children: ReactNode; y?: number; enter?: boolean; className?: string; style?: CSSProperties;
}) {
  return (
    <AnimatePresence>
      {children ? (
        <m.div key="drop" className={className} style={style}
          initial={enter && dur("base") ? { opacity: 0, transform: `translateY(${y}px)` } : false}
          animate={{ opacity: 1, transform: "none", transition: { duration: dur("base"), ease: ease("out") }, transitionEnd: { transform: "none" } }}
          exit={{ opacity: 0, transform: `translateY(${y}px)`, transition: { duration: dur("fast"), ease: ease("in") } }}>
          {children}
        </m.div>
      ) : null}
    </AnimatePresence>
  );
}

/** One view giving way to the next: the old one fades out, then the new one comes in. A new
 *  `id` is a new view. `rise` lifts it 6px as it comes, for a whole screen; `appear` animates
 *  the first view too, not only the ones that replace it. */
export function Swap({ id, children, rise = false, appear = false, className }: {
  id: string; children: ReactNode; rise?: boolean; appear?: boolean; className?: string;
}) {
  return (
    <AnimatePresence mode="wait" initial={appear}>
      <m.div key={id} className={className}
        initial={dur("base") ? { opacity: 0, transform: `translateY(${rise ? 6 : 0}px)` } : false}
        animate={{ opacity: 1, transform: "none", transition: { duration: dur("base"), ease: ease("out") }, transitionEnd: { transform: "none" } }}
        exit={{ opacity: 0, transition: { duration: dur("fast"), ease: ease("in") } }}>
        {children}
      </m.div>
    </AnimatePresence>
  );
}
