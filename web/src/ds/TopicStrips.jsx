import React from "react";
import s from "./TopicStrips.module.css";
/* Topic depth — one strip per tag: how well its tasks are known, as a stacked bar, plus
   lapses, due7, seen/total. Segments run shakiest to most solid; the scheduler's boxes stay
   behind the API, see src/strength.ts. The seven-step ramp off the accent lives in the
   module, as [data-ramp] on a segment. */
const STRIP_SORTS = {
  "stuck first": (a, b) => (b.boxes[0] + b.boxes[1]) / Math.max(1, b.seen) - (a.boxes[0] + a.boxes[1]) / Math.max(1, a.seen) || b.seen - a.seen,
  "neglected first": (a, b) => (b.total - b.seen) - (a.total - a.seen),
  "most lapses": (a, b) => b.lapses - a.lapses,
  "a–z": (a, b) => a.tag.localeCompare(b.tag),
};

function TopicStripsSort({ value, onChange }) {
  return (
    <div className={s.sorts}>
      {Object.keys(STRIP_SORTS).map((k) => (
        <button key={k} onClick={() => onChange(k)} className={s.sortBtn} data-active={k === value ? "" : undefined}>{k}</button>
      ))}
    </div>
  );
}

export function TopicStrips({ tags = [], defaultSort = "stuck first", maxHeight = 520, className, style }) {
  const [sort, setSort] = React.useState(defaultSort);
  const rows = [...tags].sort(STRIP_SORTS[sort]);
  const widest = Math.max(1, ...tags.map((t) => t.total));
  return (
    <div className={className} style={style}>
      <div className={s.head}>
        <span className={s.lede}>One strip per topic: how well you know its tasks, shakiest on the left, most solid on the right.</span>
        <div className={s.spacer} /><TopicStripsSort value={sort} onChange={setSort} />
      </div>
      {/* one table, header row included: a role="table" whose columns are a sibling div is a
          table to nobody, and its rows need the rowgroup a scrolling box would otherwise break */}
      <div role="table" aria-label="Practice spread per topic">
      <div role="rowgroup">
      <div role="row" className={s.row + " " + s.headRow}>
        <div role="columnheader" className={s.colLabel}>Tag</div><div role="columnheader" className={s.colLabel}>Spread</div>
        <div role="columnheader" className={s.colLabel} data-align="right">Lapses</div>
        <div role="columnheader" className={s.colLabel} data-align="right">Due 7</div>
        <div role="columnheader" className={s.colLabel} data-align="right">Seen</div>
      </div>
      </div>
      <div role="rowgroup" className={s.body} style={{ maxHeight }}>
        {rows.map((t) => (
          <div key={t.tag} role="row" className={s.row + " " + s.bodyRow}>
            <div role="cell" className={s.tagCell}>
              <a href={"#/?tag=" + t.tag} title={t.tag} className={s.tagLink}>{t.tag}</a>
            </div>
            <div role="cell" className={s.strip} style={{ width: (t.total / widest) * 100 + "%" }}
              title={t.tag + " — " + t.seen + " of " + t.total + " practised, " + (t.total - t.seen) + " not started"}>
              {t.boxes.map((n, i) => (n ? <div key={i} className={s.seg} data-ramp={i} style={{ flex: n }} /> : null))}
              {t.total - t.seen > 0 ? <div className={s.seg} data-rest="" style={{ flex: t.total - t.seen }} /> : null}
            </div>
            <div role="cell" className={s.num} data-tone="lapses" data-some={t.lapses ? "" : undefined}>{t.lapses || "—"}</div>
            <div role="cell" className={s.num}>{t.due7}</div>
            <div role="cell" className={s.num} data-tone="seen">{t.seen}<span className={s.of}>/{t.total}</span></div>
          </div>
        ))}
      </div>
      </div>
      <div className={s.foot}>
        <span className={s.footNote}>{tags.length} tags · strip width is the topic's size, segments run shakiest to most solid, then not started</span>
        <div className={s.spacer} />
        <div className={s.legend}>
          {[0, 1, 2, 3, 4, 5, 6].map((i) => <div key={i} className={s.chip + " " + s.seg} data-ramp={i} />)}
          <div className={s.chip + " " + s.seg} data-rest="" title="not started" />
        </div>
        <span className={s.footLabel}>shaky → solid → not started</span>
      </div>
    </div>
  );
}
