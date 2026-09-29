import type { CSSProperties, ReactNode } from "react";
import { Level } from "@app/Level";
import { Button } from "@ds/Button.jsx";
import { Icon } from "@ds/Icon.jsx";
import { Wordmark, label, mono } from "./kit";

/** The task page's 48px bar: wordmark, breadcrumb, then Progress, Settings and the theme. */
export function TopBar() {
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: 1600, height: 48, boxSizing: "border-box", padding: "0 20px", display: "flex", alignItems: "center", gap: 22, borderBottom: "1px solid var(--border)" }}>
      <Wordmark size={18} />
      <span style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-muted)" }}>
        <Icon name="ArrowLeft" />Catalogue<span style={{ color: "var(--text-faint)" }}>/</span>python<span style={{ color: "var(--text-faint)" }}>/</span><span style={{ ...mono, color: "var(--text)" }}>009</span>
      </span>
      <span style={{ flexGrow: 1 }} />
      <span style={{ color: "var(--text-muted)" }}>Progress</span>
      <span style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-muted)" }}><Icon name="Settings" />Settings</span>
      <span style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-muted)" }}><Icon name="Asleep" />Dark</span>
    </div>
  );
}

/** The header's status pill, as Task.module.css draws it. */
const pill: CSSProperties = { height: 22, display: "inline-flex", alignItems: "center", padding: "0 8px", borderRadius: 999, background: "var(--accent-tint)", fontSize: 12, fontWeight: 500, color: "var(--accent)" };

/** The one-line task header. `done` swaps the status and pauses the timer, as a pass does. */
export function TaskHeader({ timer, done = false, height = 68 }: { timer: string; done?: boolean; height?: number }) {
  return (
    <div style={{ position: "absolute", left: 0, top: 48, width: 1600, height, boxSizing: "border-box", padding: "0 24px", display: "flex", alignItems: "center", gap: 18, borderBottom: "1px solid var(--border)" }}>
      <span style={{ ...mono, fontSize: 17, color: "var(--text-faint)" }}>009</span>
      <span style={{ fontSize: 22, fontWeight: 600 }}>f-strings — aligned report columns</span>
      <span style={{ color: "var(--text-muted)" }}><Level of="easy" /></span>
      <span style={{ ...mono, fontSize: 13, color: "var(--text-muted)" }}>core/f-strings</span>
      <span style={pill}>{done ? "done" : "open"}</span>
      <span style={{ flexGrow: 1 }} />
      <span style={{ display: "flex", alignItems: "center", gap: 8, ...mono, fontSize: 19 }}>
        {done ? <span style={{ display: "flex", color: "var(--text-muted)" }}><Icon name="Pause" /></span> : null}{timer}
      </span>
      {done ? null : <span style={{ color: "var(--text-muted)", textDecoration: "underline" }}>Abandon</span>}
    </div>
  );
}

const code: CSSProperties = { ...mono, background: "var(--surface-2)", padding: "1px 5px", borderRadius: 4 };

/** The spec pane, as 009 reads. `from` skips the sections above it, for a shot further down. */
export function Spec({ width, top = 116, from = 0, children }: { width: number; top?: number; from?: number; children?: ReactNode }) {
  const parts: ReactNode[] = [
    <span key="lede" style={{ fontStyle: "italic", color: "var(--text-muted)" }}>f-string format specs — every ops report and CLI table uses them.</span>,
    <span key="why" style={{ ...label, color: "var(--accent)", marginTop: 10 }}>Why</span>,
    <span key="whyp">You run the servers for a company. Every month finance asks "how much did each service cost?" and wants it as a neat table they can read at a glance: numbers lined up under each other, commas in the thousands, always two decimals.</span>,
    <span key="get" style={{ ...label, color: "var(--accent)", marginTop: 10 }}>You get</span>,
    <span key="getp"><code style={code}>rows</code> — a list of pairs like</span>,
    <span key="getx" style={{ ...mono, fontSize: 13.5, padding: "12px 14px", border: "1px solid var(--border)", borderRadius: 6, background: "var(--surface)" }}>[(<span style={{ color: "var(--syn-string)" }}>"api"</span>, <span style={{ color: "var(--syn-number)" }}>1234.5</span>), (<span style={{ color: "var(--syn-string)" }}>"db"</span>, <span style={{ color: "var(--syn-number)" }}>7.25</span>)]</span>,
    <span key="ret" style={{ ...label, color: "var(--accent)", marginTop: 10 }}>You return</span>,
    <span key="retp">one string with one line per pair: the name on the left, the cost padded on the right so all costs line up when printed.</span>,
    <span key="rules" style={{ ...label, color: "var(--accent)", marginTop: 10 }}>Rules</span>,
    <span key="rulesp">Each row is <code style={code}>(name, value)</code>; value is a float. Return ONE string, lines joined with <code style={code}>"\n"</code>, no trailing newline.</span>,
    <span key="r1">• name left-aligned in a 14-wide column</span>,
    <span key="r2">• value right-aligned in a 12-wide column, with a thousands separator and exactly 2 decimals</span>,
  ];
  return (
    <div style={{ position: "absolute", left: 0, top, width, height: 900 - top, boxSizing: "border-box", borderRight: "1px solid var(--border)" }}>
      <div style={{ padding: "26px 24px", display: "flex", flexDirection: "column", gap: 12, fontSize: 15, lineHeight: 1.6 }}>{parts.slice(from)}</div>
      {children}
    </div>
  );
}

/** Under the editor: what this attempt has cost, then Run and Submit. */
export function RunBar({ left, top, width, submits, seed, pressed = false }: { left: number; top: number; width: number; submits: number; seed: number; pressed?: boolean }) {
  return (
    <div style={{ position: "absolute", left, top, width, height: 60, boxSizing: "border-box", padding: "0 20px", display: "flex", alignItems: "center", gap: 12, borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)", background: "var(--bg)" }}>
      <span style={{ ...mono, fontSize: 13, color: "var(--text-muted)" }}>{submits} {submits === 1 ? "submit" : "submits"} · seed {seed}</span>
      <span style={{ flexGrow: 1 }} />
      <Button variant="secondary" kbdHint="Ctrl ↵"><Icon name="Play" />Run</Button>
      <Button variant="primary" kbdHint="Ctrl ⇧ ↵" style={{ transform: pressed ? "translateY(1px)" : undefined }}><Icon name="Send" />Submit</Button>
    </div>
  );
}

/** A token of highlighted code: its text and its colour (none for plain text). */
export type Tok = [string, string?];
export const kw = (t: string): Tok => [t, "var(--syn-keyword)"];
export const str = (t: string): Tok => [t, "var(--syn-string)"];
export const br = (t: string): Tok => [t, "var(--term-magenta)"];
export const yl = (t: string): Tok => [t, "var(--warn)"];

/** Lines of tokens, cut at `chars` typed characters (all of them by default). */
export function Code({ lines, chars = Infinity, after }: { lines: Tok[][]; chars?: number; after?: (line: number) => ReactNode }) {
  let left = chars;
  return (
    <>
      {lines.map((line, i) => {
        const spans: ReactNode[] = [];
        for (const [t, c] of line) {
          if (left <= 0) break;
          const shown = t.slice(0, left);
          left -= t.length;
          spans.push(<span key={spans.length} style={c ? { color: c } : undefined}>{shown}</span>);
        }
        if (left > 0) left -= 1;   // the newline
        return <span key={i} style={{ whiteSpace: "pre", height: 19, display: "block" }}>{spans}{after?.(i)}</span>;
      })}
    </>
  );
}

/** Characters in `lines` up to and including line `n`, newlines counted. */
export const upTo = (lines: Tok[][], n: number) => lines.slice(0, n + 1).reduce((a, l) => a + l.reduce((b, [t]) => b + t.length, 0) + 1, 0);
