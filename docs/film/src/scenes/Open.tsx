import { useCurrentFrame } from "remotion";
import { Stage, Wordmark, mix, rise, useT } from "../kit";

export const TRACKS = ["python", "kubernetes", "helm", "argocd", "docker", "github-actions", "sql", "git"];

/** The banner settles into focus, its cursor starts blinking, then the line and
 *  the tracks arrive under it. */
export function Open() {
  const f = useCurrentFrame();
  const word = useT(4, 30);
  const line = useT(30, 20);
  const blink = f < 36 ? 1 : Math.floor((f - 36) / 16) % 2 ? 0.15 : 1;
  return (
    <Stage style={{ alignItems: "center", justifyContent: "center", gap: 48 }}>
      <div style={{ opacity: word, transform: `scale(${mix(word, 0.9, 1)})`, filter: `blur(${mix(word, 8, 0)}px)` }}>
        <Wordmark size={140} cursor={blink} />
      </div>
      <p style={{ margin: 0, fontSize: 44, lineHeight: 1.3, color: "var(--text-muted)", ...rise(line, 16) }}>DevOps practice, on your machine.</p>
      <div style={{ display: "flex", gap: 22, fontFamily: "var(--font-mono)", fontSize: 22, color: "var(--text-faint)" }}>
        {TRACKS.map((t, i) => <Track key={t} name={t} at={46 + i * 4} last={i === TRACKS.length - 1} />)}
      </div>
    </Stage>
  );
}

function Track({ name, at, last }: { name: string; at: number; last: boolean }) {
  const t = useT(at, 14);
  return <span style={{ display: "flex", gap: 22, ...rise(t, 10) }}><span>{name}</span>{last ? null : <span>·</span>}</span>;
}
