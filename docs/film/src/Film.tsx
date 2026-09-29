import type { ComponentType } from "react";
import { Freeze } from "remotion";
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { CUT, INOUT, SceneFrames } from "./kit";
import { Open } from "./scenes/Open";
import { Tracks } from "./scenes/Tracks";
import { Write } from "./scenes/Write";
import { Review } from "./scenes/Review";
import { Climb } from "./scenes/Climb";
import { Connections } from "./scenes/Connections";
import { Progress } from "./scenes/Progress";
import { Run } from "./scenes/Run";

/** The film in order, each scene's length in frames at 30fps. */
export const SCENES: { id: string; component: ComponentType; frames: number }[] = [
  { id: "Open", component: Open, frames: 90 },
  { id: "Tracks", component: Tracks, frames: 196 },
  { id: "Write", component: Write, frames: 380 },
  { id: "Review", component: Review, frames: 150 },
  { id: "Climb", component: Climb, frames: 126 },
  { id: "Connections", component: Connections, frames: 136 },
  { id: "Progress", component: Progress, frames: 146 },
  { id: "Run", component: Run, frames: 230 },
];

/** The loop's seam: the end card dissolves into the film's first frame, so the last frame
 *  and the first are the same picture and the loop has no jump. */
const SEAM = 16;
function Seam() {
  return <Freeze frame={0}><Open /></Freeze>;
}

export const total = SCENES.reduce((n, s) => n + s.frames, 0) - CUT * (SCENES.length - 1) + 1;

const dissolve = (key: string, frames: number) => (
  <TransitionSeries.Transition key={key} presentation={fade()} timing={linearTiming({ durationInFrames: frames, easing: INOUT })} />
);

export function Film() {
  return (
    <TransitionSeries>
      {SCENES.flatMap((s, i) => [
        ...(i ? [dissolve(`t${i}`, CUT)] : []),
        <TransitionSeries.Sequence key={s.id} durationInFrames={s.frames}>
          <SceneFrames.Provider value={s.frames}><s.component /></SceneFrames.Provider>
        </TransitionSeries.Sequence>,
      ])}
      {dissolve("seam", SEAM)}
      <TransitionSeries.Sequence durationInFrames={SEAM + 1}><Seam /></TransitionSeries.Sequence>
    </TransitionSeries>
  );
}
