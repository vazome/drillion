import type { ComponentType } from "react";
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { INOUT } from "./kit";
import { Open } from "./scenes/Open";
import { Tracks } from "./scenes/Tracks";
import { Write } from "./scenes/Write";
import { Fail } from "./scenes/Fail";
import { Review } from "./scenes/Review";
import { Climb } from "./scenes/Climb";
import { Connections } from "./scenes/Connections";
import { Progress } from "./scenes/Progress";
import { Run } from "./scenes/Run";

/** The film in order, each scene's length in frames at 30fps. */
export const SCENES: { id: string; component: ComponentType; frames: number }[] = [
  { id: "Open", component: Open, frames: 96 },
  { id: "Tracks", component: Tracks, frames: 170 },
  { id: "Write", component: Write, frames: 180 },
  { id: "Fail", component: Fail, frames: 150 },
  { id: "Review", component: Review, frames: 170 },
  { id: "Climb", component: Climb, frames: 120 },
  { id: "Connections", component: Connections, frames: 140 },
  { id: "Progress", component: Progress, frames: 150 },
  { id: "Run", component: Run, frames: 160 },
];

/** Scenes overlap by this much, crossfading. */
const CUT = 14;
export const total = SCENES.reduce((n, s) => n + s.frames, 0) - CUT * (SCENES.length - 1);

export function Film() {
  return (
    <TransitionSeries>
      {SCENES.flatMap((s, i) => [
        ...(i ? [<TransitionSeries.Transition key={`t${i}`} presentation={fade()} timing={linearTiming({ durationInFrames: CUT, easing: INOUT })} />] : []),
        <TransitionSeries.Sequence key={s.id} durationInFrames={s.frames}><s.component /></TransitionSeries.Sequence>,
      ])}
    </TransitionSeries>
  );
}
