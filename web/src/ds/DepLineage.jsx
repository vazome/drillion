import React from "react";
import { LadderMeter } from "./LadderMeter.jsx";
import { TagChip } from "./TagChip.jsx";

/** Fixed geometry, so the wires are arithmetic rather than a measured layout: every node is
 *  the same height, the title clamps to two lines, and the whole board scrolls sideways
 *  rather than reflowing. A dependency graph that reflows is a graph whose lines lie. */
const NODE_W = 216, NODE_H = 96, GAP = 16;
const BIG_W = 272, BIG_H = 118;
const WIRE = 96;                                  // the gutter the lines are drawn in
const BOARD_W = NODE_W * 2 + BIG_W + WIRE * 2;
const FAN = 9;                                     // vertical spread of the centre anchors
/** A task can unlock twenty others. Past this the column is a wall rather than a graph, so
 *  it folds — and says how many it folded, with the way back open. */
const FOLD = 8;
/** Two lines of title, always: the wires are drawn from arithmetic, so every node has to be
 *  exactly as tall as every other one. */
const titleBox = (px) => ({ height: Math.round(px * 1.25 * 2), overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" });

const numL = (n) => String(n).padStart(3, "0");
const MINI = { fontSize: "11.5px", color: "var(--text-faint)", lineHeight: 1.3 };
const MONO = { fontFamily: "var(--font-mono)", fontSize: "11.5px", color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" };
/** Top of the first card in a column of `n`, so every column shares one centre line. */
const stackTop = (n, height) => (height - (n * (NODE_H + GAP) - GAP)) / 2;
const nodeMid = (i, n, height) => stackTop(n, height) + i * (NODE_H + GAP) + NODE_H / 2;

/** One cubic from the right edge of a node to the left edge of another; the control points
 *  sit half the gutter in, which is what keeps a fan of five from crossing. */
const wire = (x1, y1, x2, y2) => {
  const dx = (x2 - x1) / 2;
  return `M${x1},${y1} C${x1 + dx},${y1} ${x2 - dx},${y2} ${x2},${y2}`;
};

function Node({ node, x, y, w, tone, href, footer, onPrefetch, children }) {
  const [hover, setHover] = React.useState(false);
  const look = tone === "passed" ? { borderColor: "var(--pass)", background: "var(--pass-bg)" }
    : tone === "blocked" ? { borderColor: "var(--border-strong)", borderStyle: "dashed", background: "var(--surface-2)" }
    : tone === "this" ? { borderColor: "var(--accent)", background: "var(--surface)", boxShadow: "0 0 0 3px var(--accent-tint)" }
    : { borderColor: "var(--border)", background: "var(--surface-2)" };
  const As = href ? "a" : "div";
  const tag = node.tags && node.tags.length ? node.tags[0] : null;
  return (
    <As
      href={href}
      // the payload is fetched on the way to the click, so the graph swaps rather than reloads
      onMouseEnter={href ? () => { setHover(true); if (onPrefetch) onPrefetch(node); } : undefined}
      onMouseLeave={href ? () => setHover(false) : undefined}
      onFocus={href && onPrefetch ? () => onPrefetch(node) : undefined}
      style={{ position: "absolute", left: x, top: y, width: w, height: tone === "this" ? BIG_H : NODE_H, boxSizing: "border-box",
        border: "1px solid", borderRadius: "var(--radius)", padding: "8px 11px", zIndex: 2, overflow: "hidden",
        display: "flex", flexDirection: "column", gap: "2px", textDecoration: "none", color: "inherit",
        ...look,
        ...(hover ? { borderColor: "var(--accent-line)", transform: "translateY(-1px)", boxShadow: "var(--shadow-card)" } : null) }}>
      <div className="tabular" style={MONO}>{numL(node.topic)}</div>
      <div title={node.title} style={{ fontSize: tone === "this" ? "15px" : "13px", fontWeight: tone === "this" ? 600 : 400, lineHeight: 1.25, textWrap: "pretty", ...titleBox(tone === "this" ? 15 : 13) }}>{node.title}</div>
      <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "auto", minWidth: 0 }}>
        {children}
        {tag ? <TagChip label={tag} small style={{ flexShrink: 0 }} /> : null}
        {footer && tone !== "this" ? <span style={{ ...MINI, color: tone === "blocked" ? "var(--warn)" : MINI.color, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{footer}</span> : null}
      </div>
      {footer && tone === "this" ? <div style={{ ...MINI, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{footer}</div> : null}
    </As>
  );
}

/** One task's lineage as the graph it is: what gates it on the left, what it gates on the
 *  right, wired to the task in the middle. A solid line is a prereq you have passed, a
 *  dashed one is what is still blocking. Nothing here refuses a task — a blocked prereq is
 *  information and a shorter way in. */
export function DepLineage({ task, requires = [], unlocks = [], ladder, hrefOf, onPrefetch, shortestPath, graphHref, onClose, style }) {
  const [unfolded, setUnfolded] = React.useState({});
  const fold = (list, key) => (unfolded[key] || list.length <= FOLD ? list : list.slice(0, FOLD));
  const req = fold(requires, "requires");
  const unl = fold(unlocks, "unlocks");

  const rows = Math.max(req.length, unl.length, 1);
  const H = Math.max(rows * (NODE_H + GAP) - GAP, BIG_H) + 8;
  const midY = H / 2;
  const colX = [0, NODE_W + WIRE, NODE_W + WIRE + BIG_W + WIRE];
  const link = (r) => (hrefOf ? hrefOf(r) : undefined);
  /** The centre card's anchors fan out, or a column of five leaves as one thick line. */
  const fan = (i, n) => midY + (i - (n - 1) / 2) * FAN;

  /** What a folded column hides, and the way back. A column that silently drops twelve
   *  tasks is a one-way door. */
  const folded = (key, all, shown) => {
    if (all.length <= FOLD) return null;
    const open = !!unfolded[key];
    return (
      <button key={key} type="button" onClick={() => setUnfolded((u) => ({ ...u, [key]: !open }))}
        style={{ background: "transparent", border: "none", padding: 0, font: "inherit", fontSize: "12.5px", color: "var(--accent)", cursor: "pointer" }}>
        {open ? `${key}: showing all ${all.length} — show ${FOLD}` : `${key}: showing ${shown.length} of ${all.length} — show all`}
      </button>
    );
  };

  const empty = (text, x) => (
    <span style={{ position: "absolute", left: x, top: midY - 9, width: NODE_W, ...MINI }}>{text}</span>
  );

  return (
    <div style={{ display: "grid", gap: "14px", ...style }}>
      {graphHref || onClose ? (
        <div style={{ display: "flex", alignItems: "baseline", gap: "12px" }}>
          <span style={{ flex: 1 }}></span>
          {graphHref ? <a href={graphHref} style={{ fontSize: "12.5px" }}>whole graph →</a> : null}
          {onClose ? <button type="button" onClick={onClose} aria-label="Close lineage" style={{ background: "transparent", border: "none", font: "inherit", fontSize: "13px", color: "var(--text-muted)", cursor: "pointer", padding: 0 }}>Close</button> : null}
        </div>
      ) : null}

      {/* `overflow-x: auto` alone computes `overflow-y` to `auto` as well, and the entrance
        * animation holds the nodes 6px low for two frames — which is a scrollbar that
        * appears and vanishes. The board's height is exact arithmetic; it never needs to
        * scroll down, so say so. */}
      <div style={{ overflowX: "auto", overflowY: "hidden" }}>
        <div key={task.topic} className="m-stagger" style={{ position: "relative", width: BOARD_W, height: H, margin: "0 auto" }}>
          <svg className="m-fade" width={BOARD_W} height={H} aria-hidden="true"
            style={{ position: "absolute", inset: 0, zIndex: 1, overflow: "visible", animationDelay: "120ms" }}>
            <defs>
              <marker id="dep-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
                <path d="M0,0 L8,4 L0,8 z" fill="var(--border-strong)" />
              </marker>
              <marker id="dep-arrow-blocked" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
                <path d="M0,0 L8,4 L0,8 z" fill="var(--text-faint)" />
              </marker>
            </defs>
            {req.map((r, i) => {
              const blocked = r.state === "blocked";
              return (
                <path key={r.topic} fill="none" strokeWidth="1.5"
                  stroke={blocked ? "var(--text-faint)" : "var(--border-strong)"}
                  strokeDasharray={blocked ? "5 4" : undefined}
                  markerEnd={`url(#dep-arrow${blocked ? "-blocked" : ""})`}
                  d={wire(colX[0] + NODE_W, nodeMid(i, req.length, H), colX[1] - 6, fan(i, req.length))} />
              );
            })}
            {unl.map((u, i) => (
              <path key={u.topic} fill="none" stroke="var(--border-strong)" strokeWidth="1.5" markerEnd="url(#dep-arrow)"
                d={wire(colX[1] + BIG_W, fan(i, unl.length), colX[2] - 6, nodeMid(i, unl.length, H))} />
            ))}
          </svg>

          {req.length
            ? req.map((r, i) => (
                <Node key={r.topic} node={r} x={colX[0]} y={stackTop(req.length, H) + i * (NODE_H + GAP)} w={NODE_W}
                  tone={r.state} href={link(r)} onPrefetch={onPrefetch}
                  footer={r.state === "passed" ? "passed" : "not passed yet"} />
              ))
            : empty("nothing — this one stands on its own", colX[0])}

          <Node node={task} x={colX[1]} y={(H - BIG_H) / 2} w={BIG_W} tone="this" footer={task.aside}>
            {ladder ? <LadderMeter box={task.box ?? 0} intervals={ladder} /> : null}
          </Node>

          {unl.length
            ? unl.map((u, i) => (
                <Node key={u.topic} node={u} x={colX[2]} y={stackTop(unl.length, H) + i * (NODE_H + GAP)} w={NODE_W}
                  href={link(u)} onPrefetch={onPrefetch}
                  footer={u.also && u.also.length
                    ? "also needs " + u.also.map(numL).join(", ")
                    : "the only block"} />
              ))
            : empty("nothing waits on this one yet", colX[2])}
        </div>
      </div>

      {requires.length > FOLD || unlocks.length > FOLD ? (
        <div style={{ display: "flex", gap: "18px", flexWrap: "wrap" }}>
          {folded("requires", requires, req)}
          {folded("unlocks", unlocks, unl)}
        </div>
      ) : null}

      {shortestPath && shortestPath.length ? (
        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap", paddingTop: "12px", borderTop: "1px solid var(--border)", fontSize: "13px", color: "var(--text-muted)" }}>
          <span style={{ fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase", color: "var(--text-muted)" }}>shortest way in</span>
          {shortestPath.map((p, i) => (
            <React.Fragment key={p.topic}>
              {i ? <span aria-hidden="true" style={{ color: "var(--text-faint)" }}>→</span> : null}
              <code className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: "12.5px", background: "var(--surface-2)", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", padding: "2px 7px", color: "var(--text)", fontVariantNumeric: "tabular-nums" }}>{numL(p.topic)}</code>
            </React.Fragment>
          ))}
        </div>
      ) : null}

      <div style={{ display: "flex", alignItems: "center", gap: "16px", flexWrap: "wrap", paddingTop: "10px", borderTop: "1px solid var(--border)", ...MINI }}>
        <span style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
          <svg width="22" height="4" aria-hidden="true"><line x1="0" y1="2" x2="22" y2="2" stroke="var(--border-strong)" strokeWidth="1.5" /></svg>
          passed
        </span>
        <span style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
          <svg width="22" height="4" aria-hidden="true"><line x1="0" y1="2" x2="22" y2="2" stroke="var(--text-faint)" strokeWidth="1.5" strokeDasharray="5 4" /></svg>
          blocking
        </span>
        <span>left to right: what gates this task, the task, what it gates</span>
      </div>
    </div>
  );
}
