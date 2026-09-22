import React from "react";
import s from "./FileTabs.module.css";

/** "templates/deployment.yaml" → ["templates/", "deployment.yaml"]: the directory is drawn
 *  quieter than the name, and a top-level file has no directory at all. */
const split = (path) => {
  const i = path.lastIndexOf("/");
  return i < 0 ? ["", path] : [path.slice(0, i + 1), path.slice(i + 1)];
};

/** The state goes into the name, not only the look: a screen reader hears which file is the
 *  learner's, that the rest are locked, and where the last run found a problem. */
const nameOf = (f) =>
  f.path + (f.readOnly ? ", part of the chart, read-only" : ", yours, editable") +
  (f.marked ? ", the last run reported a problem here" : "");

/** The line under the strip. Every variant is rendered into the same grid cell and only the
 *  active one is visible, so the row is always as tall as its longest variant: picking a tab,
 *  or a run marking one, never changes the strip's height and never moves the editor. */
function noteOf(f, mine, marked) {
  if (!f.readOnly) return { base: "yours — the only file you edit.", flag: marked ? "The last run reported a problem here." : null };
  return marked
    ? { base: "part of the chart, read-only.", flag: "The last run reported a problem here; the fix goes in " + mine + "." }
    : { base: "part of the chart, read-only — you write " + mine + ".", flag: null };
}

/** The files of one task's chart above the editor: the learner's one file first, the rest
 *  read-only. A strip that switches what the editor shows and nothing else — no tree, no
 *  closing, adding, renaming or reordering, no file-type icons. Selecting is automatic:
 *  arrow keys move and open in one step, because opening a file costs nothing. */
export function FileTabs({ files = [], active, onSelect, label = "Chart files", panelId, className, style }) {
  const base = React.useId();
  const list = React.useRef(null);
  const tabs = React.useRef([]);
  const at = Math.max(0, files.findIndex((f) => f.path === active));
  const mine = (files.find((f) => !f.readOnly) || {}).path || "";
  const firstLocked = files.findIndex((f) => f.readOnly);

  // keep the active tab in view by scrolling the strip itself — scrollIntoView could also
  // scroll the page, and the strip is the only thing allowed to move
  React.useLayoutEffect(() => {
    const el = list.current, t = tabs.current[at];
    if (!el || !t) return;
    const pad = 8;
    if (t.offsetLeft - pad < el.scrollLeft) el.scrollLeft = t.offsetLeft - pad;
    else if (t.offsetLeft + t.offsetWidth + pad > el.scrollLeft + el.clientWidth)
      el.scrollLeft = t.offsetLeft + t.offsetWidth + pad - el.clientWidth;
  }, [at, files.length]);

  const onKeyDown = (e) => {
    const n = files.length;
    if (!n) return;
    const from = Math.max(0, tabs.current.indexOf(e.target));
    const to = e.key === "ArrowRight" ? (from + 1) % n
      : e.key === "ArrowLeft" ? (from - 1 + n) % n
      : e.key === "Home" ? 0
      : e.key === "End" ? n - 1
      : null;
    if (to === null) return;
    e.preventDefault();
    tabs.current[to]?.focus();
    if (onSelect && files[to].path !== active) onSelect(files[to].path);
  };

  return (
    <div className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <div role="tablist" aria-label={label} ref={list} className={s.list} onKeyDown={onKeyDown}>
        {files.map((f, i) => {
          const [dir, name] = split(f.path);
          const on = i === at;
          return (
            <React.Fragment key={f.path}>
              {i === firstLocked ? <span aria-hidden="true" className={s.group}>Read-only</span> : null}
              <button type="button" role="tab" id={base + "-tab-" + i}
                ref={(el) => { tabs.current[i] = el; }}
                aria-selected={on} aria-controls={panelId} tabIndex={on ? 0 : -1}
                aria-label={nameOf(f)}
                data-on={on ? "" : undefined} data-mine={f.readOnly ? undefined : ""} data-marked={f.marked ? "" : undefined}
                onClick={onSelect && !on ? () => onSelect(f.path) : undefined}
                className={s.tab}>
                <span className={s.path}>
                  {dir ? <span className={s.dir}>{dir}</span> : null}
                  <span className={s.name}>{name}</span>
                </span>
                {f.readOnly ? null : <span className={s.yours}>yours</span>}
              </button>
            </React.Fragment>
          );
        })}
      </div>
      <div aria-hidden="true" className={s.notes}>
        {files.flatMap((f, i) => [false, true].map((marked) => {
          const n = noteOf(f, mine, marked);
          return (
            <p key={f.path + (marked ? "+" : "")} className={s.note}
              data-on={i === at && !!f.marked === marked ? "" : undefined}>
              <span className={s.file}>{f.path}</span> · {n.base}
              {n.flag ? <> <span className={s.flag}>{n.flag}</span></> : null}
            </p>
          );
        }))}
      </div>
    </div>
  );
}
