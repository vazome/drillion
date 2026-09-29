import { useCurrentFrame } from "remotion";
import { Stage, Wordmark, rise, useT } from "../kit";

export const TRACKS = ["python", "kubernetes", "helm", "argocd", "docker", "github-actions", "sql", "git"];

/** The banner is there from the first frame, the frame the loop dissolves back into; its cursor
 *  blinks while the line and the tracks arrive under it. */
export function Open() {
  const f = useCurrentFrame();
  const line = useT(10, 20);
  const blink = Math.floor(f / 16) % 2 ? 0.15 : 1;
  return (
    <Stage style={{ alignItems: "center", justifyContent: "center", gap: 48 }}>
      <Wordmark size={140} cursor={blink} />
      <p style={{ margin: 0, fontSize: 44, lineHeight: 1.3, color: "var(--text-muted)", ...rise(line, 16) }}>DevOps practice, on your machine.</p>
      <div style={{ display: "flex", gap: 22, fontFamily: "var(--font-mono)", fontSize: 26, color: "var(--text-muted)" }}>
        {TRACKS.map((t, i) => <Track key={t} name={t} at={20 + i * 3} last={i === TRACKS.length - 1} />)}
      </div>
    </Stage>
  );
}

function Track({ name, at, last }: { name: string; at: number; last: boolean }) {
  const t = useT(at, 14);
  return <span style={{ display: "flex", gap: 22, ...rise(t, 10) }}><span>{name}</span>{last ? null : <span style={{ color: "var(--text-faint)" }}>·</span>}</span>;
}
