import { useCurrentFrame } from "remotion";
import { Button } from "@ds/Button.jsx";
import { Icon } from "@ds/Icon.jsx";
import { Kbd } from "@ds/Kbd.jsx";
import { Level } from "@app/Level";
import { TagChip } from "@ds/TagChip.jsx";
import { Caption, Cursor, Stage, Window, label, mix, mono, usePath, useShot, useSpring } from "../kit";
import { ROW, ROWS_TOP, Sidebar, TRACK_LIST } from "../Sidebar";

/** What Today leads with once a track is picked: its first task, straight from tasks/. */
const PICKS: Record<string, { n: string; title: string; path: string; opens: [string, string][]; more: number; count: number; tags: string[] }> = {
  "All tracks": { n: "001", title: "basics — Guido's lasagna kitchen timer", path: "core/functions", opens: [["002", "bools — the Pac-Man rulebook"], ["003", "numbers — the currency exchange desk"]], more: 0, count: 385, tags: ["stdlib-ops", "classes", "files-text", "strings", "dicts", "numbers"] },
  helm: { n: "279", title: "install a chart with your own values.yaml", path: "helm/values", opens: [["280", "a NodePort through values: when a value only counts"], ["281", "requests and limits as a nested value the chart"], ["282", "a chart with no schema: the typo that renders"], ["283", "turn a feature on: a switch, and the values it"]], more: 2, count: 15, tags: ["templates", "values", "service", "deployment", "toyaml", "validation"] },
  docker: { n: "289", title: "your first Dockerfile", path: "docker/cmd", opens: [["290", "the layer cache, and why requirements.txt goes first"], ["291", "run as a numbered user, not root"], ["292", "ARG or ENV: build time, run time, or both"], ["294", "ENTRYPOINT and CMD: the program and its default"]], more: 0, count: 15, tags: ["multi-stage", "layer-cache", "pip", "security", "image-size", "cmd"] },
  kubernetes: { n: "268", title: "your first Deployment, and the two labels that have to agree", path: "kubernetes/deployment", opens: [["269", "one Pod, no controller: the smallest object"], ["275", "a StatefulSet is nothing without its headless"], ["276", "a DaemonSet has no replicas: one per node"], ["279", "install a chart with your own values.yaml"]], more: 6, count: 26, tags: ["deployment", "service", "labels", "multi-document", "networking", "workloads"] },
};
/** The clicks: which row, and on which frame. */
const CLICKS: [string, number][] = [["helm", 44], ["docker", 76], ["kubernetes", 108]];
const rowOf = (name: string) => TRACK_LIST.findIndex(([n]) => n === name);
const S = 0.86;   // the shot's scale: the whole screen, at the window's size

export function Tracks() {
  const f = useCurrentFrame();
  const enter = useSpring(4, 200, 26);
  const shot = useShot({ scale: S, x: 0, y: 0 }, { scale: 0.9, x: 20, y: 24 }, 118, 60);
  const done = CLICKS.filter(([, at]) => f >= at);
  const current = done.length ? done[done.length - 1] : (["All tracks", 0] as [string, number]);
  const prev = done.length > 1 ? done[done.length - 2][0] : "All tracks";
  const slide = useSpring(current[1], 22, 14);
  const at = done.length ? mix(slide, rowOf(prev), rowOf(current[0])) : 0;
  // the pointer, in frame pixels: the window's origin plus the row's centre at this shot's scale
  const rowY = (name: string) => 116 + (ROWS_TOP + rowOf(name) * ROW + 22) * S;
  const p = usePath([[16, 760, 780], [38, 190, rowY("helm")], [44, 190, rowY("helm")], [70, 196, rowY("docker")], [76, 196, rowY("docker")], [102, 200, rowY("kubernetes")], [130, 200, rowY("kubernetes")], [150, 420, 760]]);
  return (
    <Stage>
      <Caption eyebrow="385 TASKS" inline left={112} top={34} size={44}>Eight tracks. One ladder.</Caption>
      <Window left={112} top={116} width={1376} height={774} shot={shot} enter={enter} tilt={0}>
        <Sidebar at={at} />
        <Today pick={current[0]} since={current[1]} />
      </Window>
      <Cursor x={p.x} y={p.y} clicks={CLICKS.map(([, c]) => c)} opacity={f < 16 ? 0 : 1} />
    </Stage>
  );
}

/** Today, for the picked track. A new pick pops in as the app draws it: small to full size. */
function Today({ pick, since }: { pick: string; since: number }) {
  const d = PICKS[pick];
  const pop = useSpring(since, 12, 24);
  const arrive = since ? pop : 1;
  const popped = { opacity: Math.min(1, arrive * 1.6), transform: `scale(${mix(arrive, 0.85, 1)})`, transformOrigin: "left center" };
  return (
    <>
      <div style={{ position: "absolute", left: 334, top: 44, display: "flex", flexDirection: "column", gap: 10 }}>
        <span style={label}>Tuesday, September 29</span>
        <span style={{ fontSize: 40, fontWeight: 500, letterSpacing: "-0.01em" }}>One new pick, nothing due.</span>
      </div>
      <div style={{ position: "absolute", right: 86, top: 70, display: "flex", gap: 42 }}>
        <Stat k="done today" v="1" />
        <Stat k="practised" v="1" of="/ 385" />
      </div>

      <div style={{ position: "absolute", left: 334, top: 158, width: 756, height: 402, display: "flex", border: "1px solid var(--border)", borderRadius: 8, overflow: "hidden", background: "var(--surface)" }}>
        <div style={{ width: 175, boxSizing: "border-box", padding: "26px 24px", display: "flex", flexDirection: "column", background: "var(--accent-tint)", borderRight: "1px solid var(--border)" }}>
          <span style={{ ...mono, fontSize: 56, lineHeight: 1, color: "var(--accent)", ...popped }}>{d.n}</span>
          <span style={{ flexGrow: 1 }} />
          <span style={{ ...mono, fontSize: 12.5, color: "var(--text-muted)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{d.path}</span>
          <span style={{ marginTop: 8, color: "var(--text-muted)" }}><Level of="easy" /></span>
        </div>
        <div style={{ flexGrow: 1, boxSizing: "border-box", padding: "30px 32px 26px", display: "flex", flexDirection: "column", gap: 14 }}>
          <span style={{ ...label, color: "var(--accent)" }}>Up next · new pick</span>
          <span style={{ fontSize: 27, fontWeight: 600, lineHeight: 1.25, minHeight: 68, ...popped }}>{d.title}</span>
          <span style={{ height: 1, background: "var(--border)" }} />
          <span style={label}>Progresses into {d.opens.length + d.more} tasks</span>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", columnGap: 20, rowGap: 8, fontSize: 13.5, minHeight: 48 }}>
            {d.opens.map(([n, t]) => (
              <span key={n} style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}><span style={{ ...mono, color: "var(--text-muted)" }}>{n} </span> {t}</span>
            ))}
          </div>
          <span style={{ fontSize: 13.5, color: "var(--text-muted)", opacity: d.more ? 1 : 0 }}>and {d.more} more</span>
          <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 6 }}>
            <Button variant="primary"><Icon name="Play" />Start task</Button>
            <span style={{ color: "var(--text-muted)" }}>or press</span>
            <Kbd>Enter</Kbd>
          </div>
        </div>
      </div>

      <Ladder />

      <div style={{ position: "absolute", left: 334, top: 600, display: "flex", alignItems: "baseline", gap: 14 }}>
        <span style={label}>Pick up where you left off</span>
        <span style={{ color: "var(--text-muted)" }}>last 7 days · all passed</span>
      </div>
      <div style={{ position: "absolute", left: 334, top: 634, width: 284, height: 120, boxSizing: "border-box", padding: "20px 18px", display: "flex", flexDirection: "column", border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface)" }}>
        <span style={{ fontSize: 15, fontWeight: 500 }}>f-strings — aligned report columns</span>
        <span style={{ flexGrow: 1 }} />
        <span style={{ display: "flex", justifyContent: "space-between", ...mono, fontSize: 12.5, color: "var(--text-muted)" }}>009 · python<Icon name="ArrowRight" /></span>
      </div>

      <div style={{ position: "absolute", left: 334, top: 796, width: 1180, display: "flex", alignItems: "center", gap: 16 }}>
        <span style={{ fontSize: 22, fontWeight: 600 }}>Catalogue</span>
        {pick === "All tracks" ? null : (
          <span style={{ display: "flex", alignItems: "center", gap: 8, padding: "3px 12px", borderRadius: 999, background: "var(--accent-tint)", color: "var(--accent)", fontSize: 13.5, ...popped }}>
            {pick} · {d.count} of 385<Icon name="Close" size={12} />
          </span>
        )}
        <span style={{ flexGrow: 1 }} />
        <span style={{ width: 360, height: 36, boxSizing: "border-box", padding: "0 12px", display: "flex", alignItems: "center", gap: 8, border: "1px solid var(--control-edge)", borderRadius: 6, color: "var(--text-muted)" }}>
          <Icon name="Search" />Search titles, specs and tags<span style={{ flexGrow: 1 }} /><Kbd>/</Kbd>
        </span>
      </div>
      <div style={{ position: "absolute", left: 334, top: 848, width: 1180, display: "flex", alignItems: "center", gap: 24 }}>
        <div style={{ display: "flex", padding: 3, gap: 2, border: "1px solid var(--border)", borderRadius: 6 }}>
          {[["Any", ""], ["new", String(d.count - (pick === "All tracks" ? 1 : 0))], ["due", "0"], ["open", "0"], ["done", pick === "All tracks" ? "1" : "0"]].map(([k, v], i) => (
            <span key={k} style={{ padding: "4px 12px", borderRadius: 4, background: i ? undefined : "var(--accent-tint)", color: i ? undefined : "var(--accent)" }}>{k}{v ? ` ${v}` : ""}</span>
          ))}
        </div>
        <div style={{ display: "flex", gap: 8, ...popped, transformOrigin: "left center" }}>
          {d.tags.map((t) => <TagChip key={t} label={t} />)}
        </div>
      </div>
    </>
  );
}

function Stat({ k, v, of }: { k: string; v: string; of?: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <span style={{ fontSize: 12.5, color: "var(--text-muted)" }}>{k}</span>
      <span style={{ ...mono, fontSize: 22 }}>{v} {of ? <span style={{ fontSize: 14, color: "var(--text-muted)" }}>{of}</span> : null}</span>
    </div>
  );
}

/** Today's ladder card: seven rungs by return interval, the one task on 4d. */
export function Ladder() {
  const hue = ["warn", "warn", "accent", "accent", "accent", "pass", "pass"];
  return (
    <div style={{ position: "absolute", left: 1113, top: 158, width: 401, height: 402, boxSizing: "border-box", padding: "26px 24px", display: "flex", flexDirection: "column", gap: 16, border: "1px solid var(--border)", borderRadius: 8, background: "var(--surface)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={label}>The ladder</span>
        <span style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--accent)" }}>Your progress<Icon name="ArrowRight" /></span>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 110 }}>
        {[2, 4, 8, 16, 28, 60, 120].map((d, i) => (
          <span key={d} style={{ width: 45, height: 18 + i * 14, boxSizing: "border-box", borderRadius: 3, border: `1px dashed var(--${hue[i]})`, opacity: i === 1 ? 1 : 0.55, background: i === 1 ? "color-mix(in srgb, var(--warn) 45%, transparent)" : undefined }} />
        ))}
      </div>
      <div style={{ display: "flex", gap: 6, ...mono, fontSize: 12, color: "var(--text-muted)" }}>
        {[2, 4, 8, 16, 28, 60, 120].map((d) => <span key={d} style={{ width: 45, textAlign: "center" }}>{d}d</span>)}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <span style={{ flex: 2, height: 2, background: "var(--strength-learning)" }} /><span style={{ flex: 3, height: 2, background: "var(--strength-familiar)" }} /><span style={{ flex: 2, height: 2, background: "var(--strength-solid)" }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Level of="learning" count={1} />
        <Level of="familiar" count={0} />
        <Level of="solid" count={0} />
      </div>
      <span style={{ fontSize: 13.5, color: "var(--text-muted)" }}>A pass sends a task further out, so it comes back later.</span>
    </div>
  );
}
