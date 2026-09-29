import { useCurrentFrame } from "remotion";
import { Icon } from "@ds/Icon.jsx";
import { Kbd } from "@ds/Kbd.jsx";
import { Ring, label, mono, rise, useT } from "./kit";

const E = [
  "E               queue               283.92",
  "E               gateway             145.89",
  "E               worker              547.30",
  "E             - api              83,188.25",
  "E             ?                    -",
];

/** The result pane under the editor: idle, then the sweep while pytest runs from the Submit at
 *  `click`, then the failure from `back`, line by line, with the case that differs ringed. */
export function Result({ click: CLICK, back: BACK }: { click: number; back: number }) {
  const f = useCurrentFrame();
  const verdict = useT(BACK, 12);
  const yours = useT(BACK + 44, 18);
  const want = useT(BACK + 54, 18);
  const lines = [0, 1, 2, 3, 4].map((i) => useT(BACK + 6 + i * 3, 10));   // a fixed count: hooks, not a loop that varies
  const rest = [7, 9, 11].map((i) => useT(BACK + 6 + i * 3, 10));
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
