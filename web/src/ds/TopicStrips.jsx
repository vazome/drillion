import React from "react";
import { Icon } from "./Icon.jsx";
import s from "./TopicStrips.module.css";
/* Topic depth — one strip per tag: how well its tasks are known, as a bar in the three
   strength colours, shakiest on the left, then what is not started; seen/total and due in
   seven days beside it. `bands` names each ladder box's word — the boxes themselves stay
   behind the API, see src/strength.ts. */
const WORDS = ["learning", "familiar", "solid"];
const STRIP_SORTS = {
  "stuck first": (a, b) => b.lapses - a.lapses || (b.boxes[0] + b.boxes[1]) / Math.max(1, b.seen) - (a.boxes[0] + a.boxes[1]) / Math.max(1, a.seen) || b.seen - a.seen,
  "neglected first": (a, b) => (b.total - b.seen) - (a.total - a.seen),
  "a–z": (a, b) => a.tag.localeCompare(b.tag),
};

export function TopicStrips({ tags = [], bands = [], label, lapseLimit = 1, defaultSort = "stuck first", maxHeight = 520, className, style }) {
  const [sort, setSort] = React.useState(defaultSort);
  const rows = [...tags].sort(STRIP_SORTS[sort]);
  const known = (t) => WORDS.map((w) => t.boxes.reduce((n, c, i) => n + (bands[i] === w ? c : 0), 0));
  return (
    <div className={className} style={style}>
      <div className={s.head}>
      {label ? <h2 className={s.label}>{label}</h2> : null}
      <label className={s.sort}>
        <span className={s.sr}>Sort topics</span>
        <select value={sort} onChange={(e) => setSort(e.target.value)}>
          {Object.keys(STRIP_SORTS).map((k) => <option key={k} value={k}>{k}</option>)}
        </select>
        <Icon name="ChevronDown" size={14} />
      </label>
      </div>
      {/* one table, header row included: a role="table" whose columns are a sibling div is a
          table to nobody, and its rows need the rowgroup a scrolling box would otherwise break */}
      <div role="table" aria-label="How well you know each topic">
        <div role="rowgroup">
          <div role="row" className={s.row + " " + s.headRow}>
            <div role="columnheader">Tag</div><div role="columnheader">Spread</div>
            <div role="columnheader" data-align="right">Seen</div>
            <div role="columnheader" data-align="right">Due 7d</div>
          </div>
        </div>
        <div role="rowgroup" className={s.body} style={{ maxHeight }}>
          {rows.map((t) => {
            const [l, f, so] = known(t);
            return (
              <div key={t.tag} role="row" className={s.row + " " + s.bodyRow}>
                <div role="cell" className={s.tagCell}>
                  <a href={"#/?tag=" + t.tag} title={t.tag} className={s.tagLink}>{t.tag}</a>
                  {t.lapses >= lapseLimit ? <span className={s.stuck}>struggled {t.lapses}×</span> : null}
                </div>
                <div role="cell" className={s.strip}
                  title={t.tag + ": " + l + " learning, " + f + " familiar, " + so + " solid, " + (t.total - t.seen) + " not started"}>
                  {[l, f, so].map((n, i) => (n ? <div key={i} className={s.seg} data-of={WORDS[i]} style={{ flex: n }} /> : null))}
                  {t.total - t.seen > 0 ? <div className={s.seg} data-rest="" style={{ flex: t.total - t.seen }} /> : null}
                </div>
                <div role="cell" className={s.num}>{t.seen}/{t.total}</div>
                <div role="cell" className={s.num}>{t.due7}</div>
              </div>
            );
          })}
        </div>
      </div>
      <p className={s.foot}>{tags.length} tags · a tag opens the catalogue filtered to it</p>
    </div>
  );
}
