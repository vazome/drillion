import { useCurrentFrame } from "remotion";
import { Caption, Cursor, Stage, Window, mono, rise, toFrame, usePath, useShot, useShown, useSpring, useT } from "../kit";
import { Result } from "../Result";
import { RunBar, Spec, TaskHeader, TopBar, br, kw, str, upTo, yl, type Tok } from "../Task";

/** What gets typed, token by token. A hint token is Monaco's inlay: it types nothing and shows
 *  once its line is written. The return hint reads Any until the last line settles on str. */
const lines = (ret: string): Tok[][] => [
  [kw("def"), [" solve"], yl("("), ["rows: "], kw("list"), br("["), kw("tuple"), kw("["), kw("str"), [", "], kw("float"), kw("]"), br("]"), yl(")"), [` -> ${ret}`, "hint"], [":"]],
  [["    lines"], [": list[str]", "hint"], [" = "], yl("["), str('f"'), br("{"), ["n"], str(":<14"), br("}{"), ["v"], str(":>12.2f"), br("}"), str('"'), [" "], kw("for"), [" n, v "], kw("in"), [" rows"], yl("]")],
  [["    "], kw("return"), [" "], str('"\\n"'), ["."], ["join"], yl("("), ["lines"], yl(")")],
];
const typed = (l: Tok[][]) => l.map((line) => line.filter(([, c]) => c !== "hint"));
const TYPED = typed(lines("Any"));
const TOTAL = upTo(TYPED, 2) - 1;
const DOT = TOTAL - "join(lines)".length;   // where typing stops for the suggestions
const METHODS = ["istitle", "isupper", "join", "ljust", "lower", "lstrip", "maketrans", "partition", "removeprefix", "removesuffix", "replace", "rfind"];

const START = 24;     // first keystroke
const RATE = 1.7;     // characters a frame
const OPEN = 98;      // the suggest list opens
const ACCEPT = 168;   // join is picked
const PAN = 196;      // the camera follows the code down to the result
const CLICK = 246;    // Submit
const BACK = 268;     // the verdict comes back

const LEFT = 96, TOP = 216;
const EDITOR = { scale: 1.52, x: 673, y: 117 };   // the editor column, edge to edge
const RESULT = { scale: 1.52, x: 673, y: 358 };   // the run bar on top, the result under it

/** One screen, one shot: the editor completes the code, then the camera follows it down to the
 *  Submit, where the result names the case that failed. */
export function Write() {
  const f = useCurrentFrame();
  const enter = useSpring(0, 200, 16);
  const shot = useShot(EDITOR, RESULT, PAN, 26);
  const chars = f < ACCEPT ? Math.min(DOT, Math.max(0, (f - START) * RATE)) : Math.min(TOTAL, DOT + 4 + Math.max(0, f - ACCEPT - 2) * RATE);
  const done = chars >= TOTAL;
  const LINES = lines(done ? "str" : "Any");
  const hint1 = useT(START + upTo(TYPED, 0) / RATE + 6, 10);
  const hint2 = useT(START + upTo(TYPED, 1) / RATE + 6, 10);
  const list = useSpring(OPEN, 200, 10) * (1 - useT(ACCEPT, 4));
  const focus = f < OPEN + 10 ? 0 : f < OPEN + 16 ? 1 : 2;
  const details = useT(OPEN + 22, 12) * (1 - useT(ACCEPT, 4));
  const caret = chars >= DOT && (f < ACCEPT || done) ? (Math.floor(f / 16) % 2 ? 0 : 1) : 1;
  const row = [0, 1, 2].findIndex((i) => chars < upTo(TYPED, i));
  const submit = toFrame(shot, LEFT, TOP, 1420, 387);   // the send icon, clear of the label
  const p = usePath([[PAN + 20, submit.x + 170, submit.y + 230], [CLICK - 8, submit.x, submit.y], [CLICK, submit.x, submit.y], [CLICK + 14, submit.x + 40, submit.y + 34]]);
  return (
    <Stage>
      <Caption eyebrow="THE EDITOR" until={PAN - 8}>It knows what your value can do.</Caption>
      <Caption eyebrow="A FAILED RUN" color="var(--fail)" at={PAN + 18}>It names the case that failed.</Caption>
      <Window left={LEFT} top={TOP} width={1408} height={740} shot={shot} enter={enter}>
        <TopBar />
        <TaskHeader timer={f < 60 ? "4:07" : f < BACK ? "4:08" : "4:12"} />
        <Spec width={672} />
        <div style={{ position: "absolute", left: 673, top: 116, width: 927, height: 241, background: "var(--editor)", zIndex: 1 }}>
          <div style={{ position: "absolute", left: 0, top: 10, width: 56, display: "flex", flexDirection: "column", alignItems: "flex-end", ...mono, fontSize: 14, lineHeight: "19px", color: "var(--text-faint)" }}>
            {[1, 2, 3].map((n) => <span key={n} style={{ color: n === 3 && chars > upTo(TYPED, 1) ? "var(--text)" : undefined }}>{n}</span>)}
          </div>
          <div style={{ position: "absolute", left: 67, top: 10, ...mono, fontSize: 14, lineHeight: "19px" }}>
            <Hinted lines={LINES} chars={chars} hints={[hint1, hint2]} caret={caret} at={row === -1 ? 2 : row} />
          </div>
          {list > 0 ? (
            <>
              <div style={{ position: "absolute", left: 201, top: 67, width: 430, boxSizing: "border-box", padding: "1px 0", background: "var(--surface)", border: "1px solid var(--border-strong)", boxShadow: "var(--shadow-pop)",
                ...mono, fontSize: 14, opacity: list, transform: `translateY(${(1 - list) * -4}px)`, transformOrigin: "left top" }}>
                {METHODS.map((m, i) => (
                  <div key={m} style={{ display: "flex", alignItems: "center", gap: 6, height: 19, padding: "0 6px", background: i === focus ? "var(--accent-tint)" : undefined }}>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="var(--term-magenta)" strokeWidth="1.2" strokeLinejoin="round"><path d="M8 1.8 13.5 4.8v6.4L8 14.2 2.5 11.2V4.8z" /><path d="M2.5 4.8 8 7.8l5.5-3M8 7.8v6.4" /></svg>
                    <span>{m}</span>
                  </div>
                ))}
              </div>
              <div style={{ position: "absolute", left: 633, top: 67, width: 288, boxSizing: "border-box", padding: "8px 12px 12px", display: "flex", flexDirection: "column", gap: 10,
                background: "var(--surface)", border: "1px solid var(--border-strong)", boxShadow: "var(--shadow-pop)", fontSize: 13.5, lineHeight: 1.45, ...rise(details, -8) }}>
                <span style={{ ...mono, fontSize: 14, lineHeight: "19px", whiteSpace: "pre" }}>
                  <span style={{ color: "var(--syn-keyword)" }}>def</span>{" join(\n    iterable: Iterable["}<span style={{ color: "var(--syn-keyword)" }}>str</span>{"],\n    /\n) -> "}<span style={{ color: "var(--syn-keyword)" }}>str</span>{": ..."}
                </span>
                <span style={{ height: 1, background: "var(--border-strong)" }} />
                <span>Concatenate any number of strings.</span>
                <span>The string whose method is called is inserted in between each given string.</span>
              </div>
            </>
          ) : null}
        </div>
        <RunBar left={673} top={357} width={927} submits={f < BACK ? 0 : 1} seed={4028} pressed={f >= CLICK && f < CLICK + 4} />
        <Result click={CLICK} back={BACK} />
      </Window>
      <Cursor x={p.x} y={p.y} clicks={[CLICK]} opacity={useShown(PAN + 20, CLICK + 10)} />
    </Stage>
  );
}

/** The typed code with Monaco's inlay hints fading in behind it, and the caret on line `at`. */
function Hinted({ lines, chars, hints, caret, at }: { lines: Tok[][]; chars: number; hints: number[]; caret: number; at: number }) {
  let left = chars;
  return (
    <>
      {lines.map((line, i) => {
        const out = [];
        let whole = true;
        for (const [k, [t, c]] of line.entries()) {
          if (c === "hint") { if (whole && left > 0) out.push(<span key={k} style={{ color: "var(--text-faint)", opacity: hints[i] ?? 0 }}>{t}</span>); continue; }
          if (left <= 0) { whole = false; break; }
          out.push(<span key={k} style={c ? { color: c } : undefined}>{t.slice(0, left)}</span>);
          if (left < t.length) whole = false;
          left -= t.length;
        }
        if (left > 0) left -= 1;
        return (
          <span key={i} style={{ whiteSpace: "pre", height: 19, display: "block" }}>
            {out}{i === at ? <span style={{ display: "inline-block", width: 2, height: 17, verticalAlign: -3, background: "var(--accent)", opacity: caret }} /> : null}
          </span>
        );
      })}
    </>
  );
}
