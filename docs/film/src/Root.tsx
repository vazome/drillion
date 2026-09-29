import { Composition, Folder } from "remotion";
import { Film, SCENES, total } from "./Film";

export function Root() {
  return (
    <>
      <Composition id="Film" component={Film} durationInFrames={total} fps={30} width={1600} height={900} />
      <Folder name="Scenes">
        {SCENES.map((s) => (
          <Composition key={s.id} id={s.id} component={s.component} durationInFrames={s.frames} fps={30} width={1600} height={900} />
        ))}
      </Folder>
    </>
  );
}
