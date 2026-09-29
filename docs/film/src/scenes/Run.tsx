import { AbsoluteFill, useCurrentFrame } from "remotion";
import { Icon } from "@ds/Icon.jsx";
import { Cursor, Stage, Wordmark, mix, mono, rise, usePath, useSpring, useT } from "../kit";

const CMD = "docker run -d -p 127.0.0.1:8765:8765 -v drillion:/data ghcr.io/vazome/drillion";
const CLICK = 98;   // the theme toggle
const AT = { x: 1500, y: 58 };

/** The end card: the one command, then the theme turned over from its own toggle. Nothing says
 *  light mode; the wipe shows it. */
export function Run() {
  const f = useCurrentFrame();
  const wipe = useSpring(CLICK, 200, 30);
  const p = usePath([[64, 1180, 760], [92, AT.x - 8, AT.y + 2], [140, AT.x - 8, AT.y + 2], [160, 1260, 820]]);
  return (
    <>
      <Card light={false} />
      <AbsoluteFill style={{ clipPath: `circle(${mix(wipe, 0, 1900)}px at ${AT.x}px ${AT.y}px)` }}>
        <Card light />
      </AbsoluteFill>
      <Cursor x={p.x} y={p.y} clicks={[CLICK]} opacity={f < 64 ? 0 : 1} />
    </>
  );
}

function Card({ light }: { light: boolean }) {
  const f = useCurrentFrame();
  const word = useT(2, 20);
  const typed = Math.max(0, Math.floor((f - 16) * 2.4));
  const words = useT(52, 16);
  const url = useT(62, 16);
  return (
    <Stage light={light} style={{ alignItems: "center", justifyContent: "center", gap: 52 }}>
      <div style={{ position: "absolute", right: 48, top: 36, display: "flex", alignItems: "center", gap: 8, padding: "8px 14px", borderRadius: 6, fontSize: 20, color: "var(--text-muted)" }}>
        <Icon name={light ? "Sun" : "Asleep"} size={20} /><span>{light ? "Light" : "Dark"}</span>
      </div>
      <div style={rise(word, 16)}><Wordmark size={84} /></div>
      <div style={{ display: "flex", alignItems: "center", gap: 20, padding: "24px 36px", minWidth: 1180, boxSizing: "border-box", background: "var(--surface)", borderRadius: 12, boxShadow: "var(--shadow-card)", ...mono, fontSize: 26, whiteSpace: "pre", ...rise(word, 16) }}>
        <span style={{ color: "var(--text-faint)" }}>$</span>
        <span>
          <span style={{ color: "var(--accent)" }}>{CMD.slice(0, Math.min(typed, 10))}</span>
          <span>{CMD.slice(10, Math.min(typed, 55))}</span>
          <span style={{ color: "var(--text-muted)" }}>{CMD.slice(55, typed)}</span>
          <span style={{ display: "inline-block", width: 3, height: 30, verticalAlign: -6, background: "var(--accent)", opacity: typed < CMD.length || Math.floor(f / 16) % 2 ? 1 : 0 }} />
        </span>
      </div>
      <div style={{ display: "flex", gap: 28, fontSize: 30, color: "var(--text-muted)", ...rise(words, 12) }}>
        <span>No account</span><span style={{ color: "var(--text-faint)" }}>·</span><span>No streaks</span><span style={{ color: "var(--text-faint)" }}>·</span><span>Free</span>
      </div>
      <span style={{ ...mono, fontSize: 22, color: "var(--text-faint)", ...rise(url, 10) }}>github.com/vazome/drillion</span>
    </Stage>
  );
}
