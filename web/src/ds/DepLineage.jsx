import React from "react";
import css from "./DepLineage.module.css";
import { StatusBadge } from "./StatusBadge.jsx";
import { TagChip } from "./TagChip.jsx";

/** Fixed geometry, so the wires are arithmetic rather than a measured layout: every node is
 *  the same height, the title clamps to two lines, and the whole board scrolls sideways
 *  rather than reflowing. A dependency graph that reflows is a graph whose lines lie. */
const NODE_W = 216, NODE_H = 96, GAP = 16;
const BIG_W = 272, BIG_H = 118;
const WIRE = 96;                                  // the gutter the lines are drawn in
const BOARD_W = NODE_W * 2 + BIG_W + WIRE * 2;
/** Spacing between the centre card's anchors. At 9px two prereqs arrived under a single
 *  arrowhead and read as one edge; it opens up to this and closes again only once the
 *  column is deep enough to need the card's whole edge. */
const FAN = 26;
const EDGE = BIG_H - 28;                           // the run of that edge the anchors may use
/** A task can unlock twenty others. Past this the column is a wall rather than a graph, so
 *  it folds — and says how many it folded, with the way back open. */
const FOLD = 8;

const numL = (n) => String(n).padStart(3, "0");
/** Top of the first card in a column of `n`, so every column shares one centre line. */
const stackTop = (n, height) => (height - (n * (NODE_H + GAP) - GAP)) / 2;
const nodeMid = (i, n, height) => stackTop(n, height) + i * (NODE_H + GAP) + NODE_H / 2;

/** One cubic from the right edge of a node to the left edge of another; the control points
 *  sit half the gutter in, which is what keeps a fan of five from crossing. */
const wire = (x1, y1, x2, y2) => {
  const dx = (x2 - x1) / 2;
  return "M" + x1 + "," + y1 + " C" + (x1 + dx) + "," + y1 + " " + (x2 - dx) + "," + y2 + " " + x2 + "," + y2;
};

function Node({ node, x, y, w, tone, href, footer, onPrefetch, children }) {
  const As = href ? "a" : "div";
  const tag = node.tags && node.tags.length ? node.tags[0] : null;
  return (
    <As href={href} className={css.node} data-tone={tone} data-link={href ? "" : undefined}
      onMouseEnter={href && onPrefetch ? () => onPrefetch(node) : undefined}
      onFocus={href && onPrefetch ? () => onPrefetch(node) : undefined}
      style={{ left: x, top: y, width: w, height: tone === "this" ? BIG_H : NODE_H }}>
      <div className={css.num + " tabular"}>{numL(node.topic)}</div>
      <div title={node.title} className={css.title}>{node.title}</div>
      <div className={css.foot}>
        {children}
        {tag ? <TagChip label={tag} small className={css.chip} /> : null}
        {footer && tone !== "this" ? <span className={css.footText}>{footer}</span> : null}
      </div>
      {footer && tone === "this" ? <div className={css.footText}>{footer}</div> : null}
    </As>
  );
}

/** One task's lineage as the graph it is: what gates it on the left, what it gates on the
 *  right, wired to the task in the middle. A solid line is a prereq you have passed, a
 *  dashed one is what is still blocking. Nothing here refuses a task — a blocked prereq is
 *  information and a shorter way in. */
export function DepLineage({ task, requires = [], unlocks = [], hrefOf, onPrefetch, shortestPath, graphHref, onClose, className, style }) {
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
  const fan = (i, n) => (n < 2 ? midY : midY + (i - (n - 1) / 2) * Math.min(FAN, EDGE / (n - 1)));

  /** What a folded column hides, and the way back. A column that silently drops twelve
   *  tasks is a one-way door. */
  const folded = (key, all, shown) => {
    if (all.length <= FOLD) return null;
    const open = !!unfolded[key];
    return (
      <button key={key} type="button" className={css.foldBtn} onClick={() => setUnfolded((u) => ({ ...u, [key]: !open }))}>
        {open ? key + ": showing all " + all.length + " — show " + FOLD : key + ": showing " + shown.length + " of " + all.length + " — show all"}
      </button>
    );
  };

  const empty = (text, x) => (
    <span className={css.empty} style={{ left: x, top: midY - 9, width: NODE_W }}>{text}</span>
  );

  return (
    <div className={[css.root, className].filter(Boolean).join(" ")} style={style}>
      {graphHref || onClose ? (
        <div className={css.toolbar}>
          <span className={css.spacer}></span>
          {graphHref ? <a href={graphHref} className={css.graphLink}>whole graph →</a> : null}
          {onClose ? <button type="button" onClick={onClose} aria-label="Close lineage" className={css.closeBtn}>Close</button> : null}
        </div>
      ) : null}

      {/* `overflow-x: auto` alone computes `overflow-y` to `auto` as well, and the entrance
        * animation holds the nodes 6px low for two frames — which is a scrollbar that
        * appears and vanishes. The board's height is exact arithmetic; it never needs to
        * scroll down, so say so. */}
      <div className={css.scroll}>
        <div key={task.topic} className={css.board + " m-stagger"} style={{ width: BOARD_W, height: H }}>
          <svg className={css.wires + " m-fade"} width={BOARD_W} height={H} aria-hidden="true">
            <defs>
              <marker id="dep-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
                <path d="M0,0 L8,4 L0,8 z" fill="var(--border-strong)"></path>
              </marker>
              <marker id="dep-arrow-blocked" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
                <path d="M0,0 L8,4 L0,8 z" fill="var(--text-faint)"></path>
              </marker>
            </defs>
            {req.map((r, i) => {
              const blocked = r.state === "blocked";
              return (
                <path key={r.topic} fill="none" strokeWidth="1.5"
                  stroke={blocked ? "var(--text-faint)" : "var(--border-strong)"}
                  strokeDasharray={blocked ? "5 4" : undefined}
                  markerEnd={"url(#dep-arrow" + (blocked ? "-blocked" : "") + ")"}
                  d={wire(colX[0] + NODE_W, nodeMid(i, req.length, H), colX[1] - 6, fan(i, req.length))}></path>
              );
            })}
            {unl.map((u, i) => (
              <path key={u.topic} fill="none" stroke="var(--border-strong)" strokeWidth="1.5" markerEnd="url(#dep-arrow)"
                d={wire(colX[1] + BIG_W, fan(i, unl.length), colX[2] - 6, nodeMid(i, unl.length, H))}></path>
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
            {task.strength ? <StatusBadge status={task.strength} /> : null}
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
        <div className={css.foldRow}>
          {folded("requires", requires, req)}
          {folded("unlocks", unlocks, unl)}
        </div>
      ) : null}

      {shortestPath && shortestPath.length ? (
        <div className={css.path}>
          <span className={css.pathLabel}>shortest way in</span>
          {shortestPath.map((p, i) => (
            <React.Fragment key={p.topic}>
              {i ? <span aria-hidden="true" className={css.pathArrow}>→</span> : null}
              <code className={css.pathNum + " tabular"}>{numL(p.topic)}</code>
            </React.Fragment>
          ))}
        </div>
      ) : null}

      <div className={css.legend}>
        <span className={css.legendItem}>
          <svg width="22" height="4" aria-hidden="true"><line x1="0" y1="2" x2="22" y2="2" stroke="var(--border-strong)" strokeWidth="1.5"></line></svg>
          passed
        </span>
        <span className={css.legendItem}>
          <svg width="22" height="4" aria-hidden="true"><line x1="0" y1="2" x2="22" y2="2" stroke="var(--text-faint)" strokeWidth="1.5" strokeDasharray="5 4"></line></svg>
          blocking
        </span>
        <span>left to right: what gates this task, the task, what it gates</span>
      </div>
    </div>
  );
}
