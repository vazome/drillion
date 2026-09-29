import { useCurrentFrame } from "remotion";
import { Caption, Stage, Window, mono, rise, useShot, useSpring, useT } from "../kit";
import { RunBar, Spec, TaskHeader, TopBar, br, kw, str, upTo, yl, type Tok } from "../Task";

/** What gets typed, token by token. A hint token (colour "hint") is Monaco's inlay: it types
 *  nothing and shows once its line is written. */
const LINES: Tok[][] = [
  [kw("def"), [" solve"], yl("("), ["rows: "], kw("list"), br("["), kw("tuple"), kw("["), kw("str"), [", "], kw("float"), kw("]"), br("]"), yl(")"), [" -> Any", "hint"], [":"]],
  [["    lines"], [": list[str]", "hint"], [" = "], yl("["), str('f"'), br("{"), ["n"], str(":<14"), br("}{"), ["v"], str(":>12.2f"), br("}"), str('"'), [" "], kw("for"), [" n, v "], kw("in"), [" rows"], yl("]")],
  [["    "], kw("return"), [" "], str('"\\n"'), ["."]],
];
const typed = (l: Tok[][]) => l.map((line) => line.filter(([, c]) => c !== "hint"));
const TYPED = typed(LINES);
const METHODS = ["istitle", "isupper", "join", "ljust", "lower", "lstrip", "maketrans", "partition", "removeprefix", "removesuffix", "replace", "rfind"];

const START = 40;    // first keystroke
const RATE = 1.7;    // characters a frame
const OPEN = 118;    // the suggest list opens

export function Write() {
  const f = useCurrentFrame();
  const enter = useSpring(4, 200, 26);
  const shot = useShot({ scale: 0.86, x: 0, y: 0 }, { scale: 1.45, x: 500, y: 0 }, 22, 44);
  const chars = Math.max(0, (f - START) * RATE);
  const total = upTo(TYPED, 2) - 1;
  const hint1 = useT(START + upTo(TYPED, 0) / RATE + 6, 10);
  const hint2 = useT(START + upTo(TYPED, 1) / RATE + 6, 10);
  const list = useSpring(OPEN, 200, 10);
  const focus = f < OPEN + 10 ? 0 : f < OPEN + 16 ? 1 : 2;
  const details = useT(OPEN + 22, 12);
  const caret = chars >= total ? (Math.floor(f / 16) % 2 ? 0 : 1) : 1;
  return (
    <Stage>
      <Caption eyebrow="THE EDITOR">It knows what your value can do.</Caption>
      <Window left={96} top={232} width={1560} height={720} shot={shot} enter={enter}>
        <TopBar />
        <TaskHeader timer={f < 60 ? "3:07" : "3:08"} />
        <Spec width={672} />
        <div style={{ position: "absolute", left: 673, top: 116, width: 927, height: 594, background: "var(--editor)" }}>
          <div style={{ position: "absolute", left: 0, top: 10, width: 56, display: "flex", flexDirection: "column", alignItems: "flex-end", ...mono, fontSize: 14, lineHeight: "19px", color: "var(--text-faint)" }}>
            {[1, 2, 3].map((n) => <span key={n} style={{ color: n === 3 && chars > upTo(TYPED, 1) ? "var(--text)" : undefined }}>{n}</span>)}
          </div>
          <div style={{ position: "absolute", left: 67, top: 10, ...mono, fontSize: 14, lineHeight: "19px" }}>
            <Hinted lines={LINES} chars={chars} hints={[hint1, hint2]} caret={caret} at={TYPED.findIndex((_, i) => chars < upTo(TYPED, i)) === -1 ? 2 : TYPED.findIndex((_, i) => chars < upTo(TYPED, i))} />
          </div>
          {f >= OPEN ? (
            <>
              <div style={{ position: "absolute", left: -129, top: 67, width: 330, boxSizing: "border-box", padding: "8px 12px 12px", display: "flex", flexDirection: "column", gap: 10,
                background: "var(--surface)", border: "1px solid var(--border-strong)", boxShadow: "var(--shadow-pop)", fontSize: 13.5, lineHeight: 1.45, ...rise(details, -8), transform: `translateX(${(1 - details) * 10}px)` }}>
                <span style={{ ...mono, fontSize: 14, lineHeight: "19px", whiteSpace: "pre" }}>
                  <span style={{ color: "var(--syn-keyword)" }}>def</span>{" join(\n    iterable: Iterable[LiteralString],\n    /\n) -> LiteralString: ...\n\n"}
                  <span style={{ color: "var(--syn-keyword)" }}>def</span>{" join(\n    iterable: Iterable["}<span style={{ color: "var(--syn-keyword)" }}>str</span>{"],\n    /\n) -> "}<span style={{ color: "var(--syn-keyword)" }}>str</span>{": ..."}
                </span>
                <span style={{ height: 1, background: "var(--border-strong)" }} />
                <span>Concatenate any number of strings.</span>
                <span>The string whose method is called is inserted in between each given string. The result is returned as a new string.</span>
                <span>Example: '.'.join(['ab', 'pq', 'rs']) -&gt; 'ab.pq.rs'</span>
              </div>
              <div style={{ position: "absolute", left: 201, top: 67, width: 430, boxSizing: "border-box", padding: "1px 0", background: "var(--surface)", border: "1px solid var(--border-strong)", boxShadow: "var(--shadow-pop)",
                ...mono, fontSize: 14, opacity: list, transform: `translateY(${(1 - list) * -4}px)`, transformOrigin: "left top" }}>
                {METHODS.map((m, i) => (
                  <div key={m} style={{ display: "flex", alignItems: "center", gap: 6, height: 19, padding: "0 6px", background: i === focus ? "var(--accent-tint)" : undefined }}>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="var(--term-magenta)" strokeWidth="1.2" strokeLinejoin="round"><path d="M8 1.8 13.5 4.8v6.4L8 14.2 2.5 11.2V4.8z" /><path d="M2.5 4.8 8 7.8l5.5-3M8 7.8v6.4" /></svg>
                    <span>{m}</span>
                  </div>
                ))}
              </div>
            </>
          ) : null}
        </div>
        <RunBar left={673} top={710} width={927} submits={0} seed={8189} />
      </Window>
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
