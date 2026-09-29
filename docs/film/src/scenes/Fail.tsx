import { useCurrentFrame } from "remotion";
import { Icon } from "@ds/Icon.jsx";
import { Kbd } from "@ds/Kbd.jsx";
import { Caption, Cursor, Ring, Stage, Window, label, mono, rise, toFrame, useShot, useSpring, useT } from "../kit";
import { RunBar, Spec, TaskHeader, TopBar } from "../Task";

const CLICK = 24;   // Submit
const BACK = 46;    // the verdict comes back
const LEFT = 150, TOP = 216;
const E = [
  "E           AssertionError: assert 'queue               283.92\\ngateway             145.89\\nworker              547.30\\napi               83188.25\\ncache               305.64' == 'queue               283.92\\ngateway             145.89\\nworker              547.30\\napi              83,188.25\\ncache               305.64'",
  "E               queue               283.92",
  "E               gateway             145.89",
  "E               worker              547.30",
  "E             - api              83,188.25",
  "E             ?                    -",
];

export function Fail() {
  const f = useCurrentFrame();
  const enter = useSpring(0, 200, 20);
  const shot = useShot({ scale: 1.25, x: 560, y: 290 }, { scale: 1.3, x: 590, y: 360 }, 50, 80);
  const submit = toFrame(shot, LEFT, TOP, 1486, 387);
  const p = { x: f < 8 ? submit.x + 220 : submit.x, y: f < 8 ? submit.y + 140 : submit.y };
  const move = useT(6, 16);
  const cursor = { x: p.x + (1 - move) * 220 * (f >= 8 ? 1 : 0), y: p.y + (1 - move) * 140 * (f >= 8 ? 1 : 0) };
  return (
    <Stage>
      <Caption eyebrow="A FAILED RUN" color="var(--fail)" left={150}>It names the case that failed.</Caption>
      <Window left={LEFT} top={TOP} width={1300} height={740} shot={shot} enter={enter}>
        <TopBar />
        <TaskHeader timer="4:12" />
        <Spec width={672} from={6} />
        <div style={{ position: "absolute", left: 673, top: 116, width: 927, height: 241, background: "var(--editor)" }}>
          <div style={{ position: "absolute", left: 67, top: 10, ...mono, fontSize: 14, lineHeight: "19px", whiteSpace: "pre" }}>
            <div><span style={{ color: "var(--syn-keyword)" }}>def</span> solve(rows: list[tuple[str, float]])<span style={{ color: "var(--text-faint)" }}> -&gt; str</span>:</div>
            <div>    lines<span style={{ color: "var(--text-faint)" }}>: list[str]</span> = [<span style={{ color: "var(--syn-string)" }}>f"{"{"}n:&lt;14{"}{"}v:&gt;12.2f{"}"}"</span> <span style={{ color: "var(--syn-keyword)" }}>for</span> n, v <span style={{ color: "var(--syn-keyword)" }}>in</span> rows]</div>
            <div>    <span style={{ color: "var(--syn-keyword)" }}>return</span> <span style={{ color: "var(--syn-string)" }}>"\n"</span>.join(lines)</div>
          </div>
        </div>
        <RunBar left={673} top={357} width={927} submits={f < BACK ? 0 : 1} seed={4028} pressed={f >= CLICK && f < CLICK + 4} />
        <Result />
      </Window>
      <Cursor x={cursor.x} y={cursor.y} clicks={[CLICK]} opacity={f < 6 || f > BACK + 20 ? 0 : 1} />
    </Stage>
  );
}

/** The result pane: idle, then the sweep while pytest runs, then the failure, line by line. */
function Result() {
  const f = useCurrentFrame();
  const verdict = useT(BACK, 12);
  const yours = useT(BACK + 44, 18);
  const want = useT(BACK + 54, 18);
  const lines = [0, 1, 2, 3, 4, 5].map((i) => useT(BACK + 6 + i * 3, 10));   // a fixed count: hooks, not a loop that varies
  const rest = [8, 10, 12].map((i) => useT(BACK + 6 + i * 3, 10));
  const box = { position: "absolute", left: 673, top: 417, width: 927, height: 483, boxSizing: "border-box", padding: "18px 20px", overflow: "hidden" } as const;
  if (f < CLICK + 2) return (
    <div style={box}>
      <strong style={{ fontSize: 17, fontWeight: 600 }}>Nothing run yet.</strong>
      <p style={{ margin: "10px 0", color: "var(--text-muted)" }}>Run checks your code and costs nothing. Submit is the one that grades it and moves the card.</p>
      <p style={{ margin: 0, display: "flex", gap: 20, color: "var(--text-muted)" }}><span>Run <Kbd>Ctrl ↵</Kbd></span><span>Submit <Kbd>Ctrl ⇧ ↵</Kbd></span></p>
    </div>
  );
  if (f < BACK) {
    const sweep = ((f - CLICK) % 22) / 22;
    return (
      <div style={box}>
        <span style={{ position: "absolute", top: 0, bottom: 0, width: "28%", left: `${-40 + sweep * 380}%`, background: "linear-gradient(90deg, transparent, var(--accent-tint), transparent)" }} />
        <strong style={{ position: "relative", fontSize: 17, fontWeight: 600 }}>Checking your code…</strong>
        <p style={{ position: "relative", margin: "10px 0", color: "var(--text-muted)" }}>Pytest, on freshly generated data.</p>
      </div>
    );
  }
  return (
    <div style={{ ...box, display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, ...rise(verdict, 10) }}>
        <span style={{ display: "flex", alignItems: "center", gap: 6, padding: "3px 10px", borderRadius: 6, background: "var(--fail-bg)", color: "var(--fail)", fontWeight: 500 }}><Icon name="CloseOutline" size={14} />Not yet</span>
        <span style={{ color: "var(--text-muted)" }}>Submit 1 · the card has not moved</span>
      </div>
      <div style={{ ...mono, fontSize: 14, lineHeight: "19.5px", whiteSpace: "pre-wrap" }}>
        {E.map((l, i) => <div key={i} style={{ opacity: lines[i] }}>{l}</div>)}
      </div>
      <span style={{ ...label, marginTop: 4, opacity: rest[0] }}>Input</span>
      <div style={{ padding: "9px 12px", borderRadius: 6, background: "var(--surface-2)", ...mono, fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", opacity: rest[0] }}>
        <span style={{ color: "var(--text-faint)" }}>rows = </span>[('queue', 283.92), ('gateway', 145.89), ('worker', 547.3), ('api', 83188.25), ('cache', 305.64)]
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", columnGap: 14, rowGap: 8, marginTop: 4, ...rise(rest[1], 8) }}>
        <span style={label}>Your output</span>
        <span style={label}>Expected</span>
        <Out bg="var(--fail-bg)" fg="var(--fail)" head={"'queue               283.92\\ngateway             145.89\\nworker              547.30\\napi               "} mark="83188.25" t={yours} />
        <Out bg="var(--pass-bg)" fg="var(--pass)" head={"'queue               283.92\\ngateway             145.89\\nworker              547.30\\napi              "} mark="83,188.25" t={want} />
      </div>
      <span style={{ ...mono, fontSize: 14, color: "var(--text-faint)", opacity: rest[2] }}>assert solve(list(rows)) == _reference(rows)</span>
    </div>
  );
}

/** One side of the case: the repr as it wraps, and a ring drawn around the part that differs. */
function Out({ bg, fg, head, mark, t }: { bg: string; fg: string; head: string; mark: string; t: number }) {
  return (
    <div style={{ display: "flex", gap: 14, padding: "9px 12px", borderRadius: 6, background: bg, color: fg, ...mono, fontSize: 14, lineHeight: "21px" }}>
      <span style={{ color: "var(--text-faint)" }}>1</span>
      <span style={{ whiteSpace: "pre-wrap" }}>{head}<span style={{ position: "relative", display: "inline-block" }}>{mark}<Ring t={t} w={mark.length * 8.4} h={21} pad={3} /></span>{"\\ncache               305.64'"}</span>
    </div>
  );
}
