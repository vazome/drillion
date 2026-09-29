import { AbsoluteFill, useCurrentFrame } from "remotion";
import { Icon } from "@ds/Icon.jsx";
import { Cursor, INOUT, Stage, Wordmark, mix, mono, rise, usePath, useShown, useSpring, useT } from "../kit";

const CMD = "docker run -d -p 127.0.0.1:8765:8765 -v drillion:/data ghcr.io/vazome/drillion";
const CLICK = 92;   // the theme toggle
const AT = { x: 1470, y: 60 };
const MORPH = 180;   // the rest leaves and the wordmark settles where the film's first frame has it
const GROW = 140 / 84, DROP = 67;   // Open's wordmark size over this one's, and how far below its centre

/** The end card: the one command, then the theme turned over from its own toggle. Nothing says
 *  light mode; the wipe shows it. It then holds still until the film dissolves back to its start. */
export function Run() {
  const wipe = useSpring(CLICK, 200, 30);
  const p = usePath([[58, 1260, 820], [CLICK - 8, AT.x, AT.y], [CLICK, AT.x, AT.y], [CLICK + 26, AT.x + 60, AT.y + 110]]);
  return (
    <>
      <Card light={false} />
      <AbsoluteFill style={{ clipPath: `circle(${mix(wipe, 0, 1900)}px at ${AT.x}px ${AT.y}px)` }}>
        <Card light />
      </AbsoluteFill>
      <Cursor x={p.x} y={p.y} clicks={[CLICK]} opacity={useShown(58, CLICK + 20)} />
    </>
  );
}

function Card({ light }: { light: boolean }) {
  const f = useCurrentFrame();
  const word = useT(2, 20);
  const typed = Math.max(0, Math.floor((f - 16) * 2.4));
  const words = useT(52, 16);
  const url = useT(62, 16);
  const rest = 1 - useT(MORPH, 12);
  const glide = useT(MORPH, 26, INOUT);
  return (
    <Stage light={light} style={{ alignItems: "center", justifyContent: "center", gap: 52 }}>
      <div style={{ position: "absolute", right: 48, top: 36, opacity: rest, display: "flex", alignItems: "center", gap: 10, padding: "8px 16px", border: "1px solid var(--border)", borderRadius: 999, fontSize: 24, color: "var(--text-muted)" }}>
        <Icon name={light ? "Sun" : "Asleep"} size={24} /><span>{light ? "Light" : "Dark"}</span>
      </div>
      <div style={{ opacity: word, transform: `translateY(${mix(word, 16, 0) + DROP * glide}px) scale(${mix(glide, 1, GROW)})` }}><Wordmark size={84} /></div>
      <div style={{ display: "flex", alignItems: "center", gap: 20, padding: "24px 36px", width: 1340, boxSizing: "border-box", background: "var(--surface)", borderRadius: 12, boxShadow: "var(--shadow-card)", ...mono, fontSize: 26, whiteSpace: "pre", ...rise(word, 16), opacity: word * rest }}>
        <span style={{ color: "var(--text-faint)" }}>$</span>
        <span>
          <span style={{ color: "var(--accent)" }}>{CMD.slice(0, Math.min(typed, 10))}</span>
          <span>{CMD.slice(10, Math.min(typed, 55))}</span>
          <span style={{ color: "var(--text-muted)" }}>{CMD.slice(55, typed)}</span>
          <span style={{ display: "inline-block", width: 3, height: 30, verticalAlign: -6, background: "var(--accent)", opacity: typed < CMD.length || Math.floor(f / 16) % 2 ? 1 : 0 }} />
        </span>
      </div>
      <div style={{ display: "flex", gap: 28, fontSize: 30, color: "var(--text-muted)", ...rise(words, 12), opacity: words * rest }}>
        <span>No account</span><span style={{ color: "var(--text-faint)" }}>·</span><span>No streaks</span><span style={{ color: "var(--text-faint)" }}>·</span><span>Free</span>
      </div>
      <span style={{ ...mono, fontSize: 26, color: "var(--text-muted)", ...rise(url, 10), opacity: url * rest }}>github.com/vazome/drillion</span>
    </Stage>
  );
}
