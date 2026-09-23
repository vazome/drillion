import { useEffect, useState } from "react";
import { DueForecast, EmptyState, PracticeHeatmap, StatusBadge, Table, TopicStrips } from "./ds/index.js";
import { api, type Progress as Payload } from "./api";
import { taskHref } from "./Deps";
import { Level } from "./Level";
import { bands, strength, tally } from "./strength";
import s from "./Progress.module.css";

/** "2026-08-26" → "26 Aug". Parsed at local midnight so the day never slips a timezone. */
const day = (iso: string) => new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { day: "numeric", month: "short" });
const WORDS = ["learning", "familiar", "solid"] as const;

const LOG_COLS = [
  { key: "date", label: "Date", width: "68px", mono: true, muted: true, render: (r: LogRow) => day(r.date) },
  { key: "slug", label: "Task", mono: true, render: (r: LogRow) => <a href={taskHref(r.slug)} title={r.slug} className={s.clip}>{r.slug}</a> },
  { key: "grade", label: "Grade", width: "112px", render: (r: LogRow) => <StatusBadge status={r.grade} /> },
  { key: "attempts", label: "Tries", align: "right" as const, mono: true, width: "60px", muted: true },
  { key: "time", label: "Active", align: "right" as const, mono: true, width: "68px" },
];
type LogRow = Payload["log"][number];

/** "Started early August", from the first day anything passed; nothing when it is older
 *  than the year the grid shows. */
function started(days: Payload["days"], today: string) {
  const first = Object.keys(days).filter((d) => days[d] > 0).sort()[0];
  if (!first) return "No passes yet. Every square fills in as you practise.";
  const at = new Date(`${first}T00:00:00`);
  if (Date.parse(`${today}T00:00:00`) - at.getTime() > 365 * 86400000) return "Passes per day.";
  const part = at.getDate() <= 10 ? "early" : at.getDate() <= 20 ? "mid" : "late";
  return `Passes per day. Started ${part} ${at.toLocaleDateString(undefined, { month: "long" })}.`;
}

export function Progress() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api<Payload>("/progress").then(setData).catch((e) => setError(e.message)); }, []);

  if (error) return <EmptyState message={`Could not load progress: ${error}`} />;
  if (!data) return <EmptyState message="Loading…" />;

  const tags = Object.entries(data.per_tag).map(([tag, t]) => ({ tag, ...t }));
  const known = tally(data.boxes, data.ladder);
  const band = bands(data.ladder);
  // whole minutes: the log is a record of sittings, not a stopwatch
  const logRows = [...data.log].reverse().map((row, i) => ({ ...row, id: i, time: `${Math.max(1, Math.round(row.secs / 60))}m` }));

  return (
    <div className={s.page}>
      <header className={s.head}>
        <div className={s.headText}>
          <span className={s.eyebrow}>{new Date(`${data.today}T00:00:00`).toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" })}</span>
          <h1 className={s.h1}>Where you are on the ladder.</h1>
        </div>
        <dl className={s.stats}>
          <div><dt>days practised</dt><dd>{data.practised}<span> of {data.window}</span></dd></div>
          <div><dt>due today</dt><dd>{data.due}</dd></div>
          <div><dt>practised</dt><dd>{data.seen}<span> / {data.total}</span></dd></div>
        </dl>
      </header>

      <section aria-labelledby="known-h" className={s.card}>
        <div className={s.between}>
          <h2 id="known-h" className={s.eyebrow}>How well you know them</h2>
          <span className={s.mono}>{data.seen} practised · {data.total - data.seen} not started</span>
        </div>
        <div aria-hidden="true" className={s.spread}>
          {WORDS.map((k) => known[k] ? <span key={k} data-of={k} style={{ width: `${(known[k] / data.total) * 100}%` }} /> : null)}
        </div>
        <div className={s.words}>
          {WORDS.map((k) => (
            <div key={k} data-of={k} className={s.word}>
              <Level of={k} />
              <span className={s.big}>{known[k]} <span>{known[k] === 1 ? "task" : "tasks"}</span></span>
              <span className={s.small}>{band[k]}</span>
            </div>
          ))}
        </div>
        <p className={s.muted}>Every task you pass moves further out, so it comes back later; one you struggle through moves back in and returns sooner. A sailing pass counts double.</p>
      </section>

      <section aria-labelledby="due-h" className={s.card}>
        <div className={s.band}>
          <h2 id="due-h" className={s.eyebrow}>Due load · next 14 days</h2>
          <span className={s.muted}>The line is the daily cap of {data.cap}; a day above it spills into the next.</span>
        </div>
        <DueForecast forecast={data.forecast} cap={data.cap} today={data.today} />
      </section>

      <section aria-labelledby="hm-h" className={s.card}>
        <div className={s.band}>
          <h2 id="hm-h" className={s.eyebrow}>Practice · last 12 months</h2>
          <span className={s.muted}>{started(data.days, data.today)}</span>
        </div>
        <PracticeHeatmap days={data.days} today={data.today} />
      </section>

      <div className={s.pair}>
        <section className={s.card} data-tight="">
          <TopicStrips tags={tags} label="Topic depth" lapseLimit={data.lapse_limit} bands={data.ladder.map((_, i) => strength(i, true, data.ladder)!)} />
        </section>
        <section aria-labelledby="log-h" className={s.card} data-tight="">
          <h2 id="log-h" className={s.eyebrow}>Last 30 sessions</h2>
          <div className={s.log}>
            <Table columns={LOG_COLS} rows={logRows} emptyMessage="No passes logged yet. The first one lands here." />
          </div>
          <p className={s.small}>QUICK · first try, under par · PASS · STRUGGLED · abandoned</p>
        </section>
      </div>
    </div>
  );
}
