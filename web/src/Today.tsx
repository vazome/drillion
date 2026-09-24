import { useEffect, type ReactNode } from "react";
import { Button, EmptyState, Icon, Kbd, NoticeBanner, TagChip, TaskPath } from "./ds/index.js";
import type { Catalogue as Payload, Row } from "./api";
import { Level } from "./Level";
import { taskHref } from "./Deps";
import { plural, topicNo } from "./format";
import { inDays, strength, tally } from "./strength";
import s from "./Today.module.css";

const DAY = 86400000;
const WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"];
const word = (n: number) => WORDS[n] ?? String(n);
const count = (n: number, noun: string) => `${word(n)} ${noun}${n === 1 ? "" : "s"}`;
const cap = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);
const FIRST_RUN = "drillion-first-run";
const HOW_IT_WORKS = "https://github.com/vazome/drillion/blob/main/docs/how-it-works.md";
// the ladder drawn as a staircase: each rung a step higher than the last, whatever it holds
const RUNG = [14, 24, 34, 46, 58, 74, 92];

/** Today as a LOCAL YYYY-MM-DD, which parses back to the same UTC midnight `due` does. */
const localToday = () => new Date().toLocaleDateString("en-CA");

/** "4 days overdue" / "due today" / "due in 3 days". */
function dueText(row: Row) {
  const days = Math.round((Date.parse(row.due) - Date.parse(localToday())) / DAY);
  if (days === 0) return "due today";
  return days < 0 ? `${plural(-days, "day")} overdue` : `due in ${plural(days, "day")}`;
}

/** The day in one sentence: reviews first, then new picks, both numbers said out loud. */
export function headline(review: number, due: number, fresh: number) {
  const picks = count(fresh, "new pick");
  if (!due) return fresh ? `${cap(picks)}, nothing due.` : "Nothing due, nothing new.";
  const capped = review < due;
  const reviews = capped ? `${review} of ${due} due reviews today` : count(review, "review");
  if (!fresh) return `${cap(reviews)}, no new picks.`;
  return `${cap(reviews)}${capped ? "," : ""} and ${picks}.`;
}

/** The one reason there are no new picks, and the way back out of it. */
function noPicks(no: NonNullable<Payload["today"]["no_new"]>, today: Payload["today"], focus: string | null, by: Map<string, Row>) {
  const link = (slug: string) => {
    const r = by.get(slug);
    return r ? <a href={taskHref(slug)}>{topicNo(r.topic)} {r.title}</a> : null;
  };
  switch (no.why) {
    case "cap": return { focus: false, message: <>That is today's new material, {plural(today.done_today, "new task")} done. {plural(no.ready, "task")} unlocked and waiting for tomorrow.</> };
    case "prereqs": return {
      focus: false,
      message: <>Every unseen task{focus ? <> under “{focus}”</> : null} is waiting on a prereq. The nearest is {link(no.nearest)}; pass {(by.get(no.nearest)?.blocked ?? [])
        .map((slug, i) => <span key={slug}>{i ? ", " : ""}{link(slug)}</span>)} first.</>,
    };
    case "focus": return { focus: true, message: <>Nothing unseen is left under the focus “{focus}”: every task it covers is already started.</> };
    case "done": return { focus: false, message: <>Nothing unseen is left: you have opened every task in the catalogue. Reviews are the work now.</> };
  }
  return no satisfies never;
}

/** "The first of 15 in docker": where a task sits in its track. */
function place(row: Row, rows: Row[]) {
  const group = row.track ?? row.tier;
  if (!group) return null;
  const peers = rows.filter((r) => (r.track ?? r.tier) === group).sort((a, b) => a.topic - b.topic);
  const n = peers.indexOf(row) + 1;
  const suffix: Partial<Record<Intl.LDMLPluralRule, string>> = { one: "st", two: "nd", few: "rd" };
  const nth = n === 1 ? "first" : `${n}${suffix[new Intl.PluralRules("en", { type: "ordinal" }).select(n)] ?? "th"}`;
  return `The ${nth} of ${peers.length} in ${group}.`;
}

function UpNext({ data, by, queue, focus, onFocus, onAllDue }: {
  data: Payload; by: Map<string, Row>; queue: Row[]; focus: string | null;
  onFocus: (tag: string | null) => void; onAllDue: () => void;
}) {
  const { today, stats, tasks } = data;
  const empty = today.no_new ? noPicks(today.no_new, today, focus, by) : null;
  const head = queue[0];
  if (!head) {
    return (
      <section aria-labelledby="next-h" className={s.card} data-empty="">
        <div className={s.nextBody}>
          <h2 id="next-h" className={s.eyebrow}>Up next</h2>
          <p className={s.nextNote}>{empty?.message ?? "Nothing is waiting today."}</p>
          {empty?.focus ? <div><Button variant="secondary" onClick={() => onFocus(null)}>Clear focus</Button></div> : null}
        </div>
      </section>
    );
  }
  const review = today.review.includes(head.slug);
  const opens = tasks.filter((r) => r.prereqs?.includes(head.topic)).sort((a, b) => a.topic - b.topic);
  const needs = (head.prereqs ?? []).map(topicNo);
  const known = strength(head.box, !!head.seen, stats.ladder);
  const then = queue.slice(1, 4);
  return (
    <section aria-labelledby="next-h" className={s.card}>
      <div className={s.number}>
        <span className={s.big}>{topicNo(head.topic)}</span>
        <span className={s.grow} />
        <TaskPath tier={head.tier} track={head.track} tags={head.tags.slice(0, 1)} />
        <Level of={head.difficulty} />
      </div>
      <div className={s.nextBody}>
        <h2 id="next-h" className={s.eyebrow} data-accent="">Up next · {review ? "review" : "new pick"}</h2>
        <p className={s.title}>{head.title}</p>
        <p className={s.muted}>
          {review ? <>{cap(dueText(head))}. {known ? <>Last seen as <Level of={known} />.</> : null}</>
            : <>{needs.length ? `Builds on ${needs.join(" · ")}.` : "No prereqs."} {place(head, tasks)}</>}
        </p>
        {opens.length ? (
          <div className={s.opens}>
            <span className={s.eyebrow}>Progresses into {plural(opens.length, "task")}</span>
            <ul>
              {opens.slice(0, 4).map((r) => <li key={r.slug}><span className={s.mono}>{topicNo(r.topic)}</span><span className={s.clip}>{r.title}</span></li>)}
            </ul>
            {opens.length > 4 ? <span className={s.muted}>and {opens.length - 4} more</span> : null}
          </div>
        ) : null}
        <span className={s.grow} />
        <div className={s.start}>
          <a href={taskHref(head.slug)} className={s.primary}><Icon name="Play" size={14} />Start task</a>
          <span className={s.muted}>or press <Kbd>Enter</Kbd></span>
        </div>
        <p className={s.foot}>
          <span>1 of {queue.length} today</span>
          {then.length ? <> · then {then.map((r, i) => <span key={r.slug}>{i ? " · " : ""}<a href={taskHref(r.slug)} title={r.title}>{topicNo(r.topic)}</a></span>)}</> : null}
          {today.due_total ? <> · <button type="button" onClick={onAllDue} className={s.link}>all due<Icon name="ArrowRight" size={14} /></button></> : null}
        </p>
        {empty && today.new.length === 0 ? <p className={s.foot}>{empty.message}</p> : null}
      </div>
    </section>
  );
}

function Ladder({ stats }: { stats: Payload["stats"] }) {
  const words = stats.ladder.map((_, i) => strength(i, true, stats.ladder)!);
  const known = tally(stats.boxes, stats.ladder);
  const groups = (["learning", "familiar", "solid"] as const).map((k) => ({ k, rungs: words.filter((w) => w === k).length }));
  const now = new Date();
  const days = stats.week.map((_, i) => new Date(now.getFullYear(), now.getMonth(), now.getDate() - (stats.week.length - 1 - i)));
  return (
    <section aria-labelledby="ladder-h" className={s.ladder}>
      <div className={s.between}>
        <h2 id="ladder-h" className={s.eyebrow}>The ladder</h2>
        <a href="#/progress" className={s.more}>Your progress<Icon name="ArrowRight" size={14} /></a>
      </div>
      <div className={s.rungs} role="img" aria-label={`Tasks by how soon they come back: ${stats.ladder.map((d, i) => `${stats.boxes[i]} in ${d} days`).join(", ")}.`}>
        {stats.ladder.map((d, i) => (
          <span key={d} className={s.rung} data-of={words[i]} data-empty={stats.boxes[i] ? undefined : ""} style={{ height: RUNG[i] ?? RUNG.at(-1) }}>
            {stats.boxes[i] ? <span className={s.held}>{stats.boxes[i]}</span> : null}
          </span>
        ))}
      </div>
      <div className={s.axis} aria-hidden="true">{stats.ladder.map((d) => <span key={d}>{d}d</span>)}</div>
      <div className={s.groups} style={{ gridTemplateColumns: groups.map((g) => `${g.rungs}fr`).join(" ") }}>
        {groups.map(({ k }) => <span key={k} data-of={k}><Level of={k} count={known[k]} /></span>)}
      </div>
      <p className={s.muted}>{stats.seen
        ? "Each rung is how long until a task comes back. A pass moves it up a rung; a struggle moves it back down."
        : "Empty for now. Pass a task and it lands on the first rung; each rung is how long until it comes back."}</p>
      <div className={s.week}>
        <div className={s.between}>
          <span className={s.muted}>Days practised</span>
          <span className={s.mono}><span className={s.strong}>{stats.practised}</span> of {stats.window}</span>
        </div>
        <div className={s.days}>
          {days.map((d, i) => {
            const isToday = i === days.length - 1;
            return (
              <span key={i} title={`${d.toLocaleDateString(undefined, { weekday: "long" })}: ${stats.week[i] ? "practised" : "not practised"}`}>
                <span className={s.day} data-on={stats.week[i] || undefined} data-today={isToday || undefined} />
                <span className={s.weekday} data-today={isToday || undefined}>{d.toLocaleDateString(undefined, { weekday: "narrow" })}</span>
              </span>
            );
          })}
        </div>
      </div>
    </section>
  );
}

/** Pick up where you left off: what shares a state is said once, in the band. */
function Recent({ rows, window }: { rows: Row[]; window: number }) {
  const shared = !rows.length ? null
    : rows.every((r) => !r.seen) ? "none passed yet"
    : rows.every((r) => r.status === "done") ? "all passed"
    : rows.every((r) => r.status === "open") ? "all still open"
    : null;
  return (
    <section aria-labelledby="recent-h" className={s.section}>
      <div className={s.band}>
        <h2 id="recent-h" className={s.eyebrow}>Pick up where you left off</h2>
        <span className={s.muted}>last {window} days{shared ? ` · ${shared}` : ""}</span>
      </div>
      {rows.length ? (
        <div className={s.recent}>
          {rows.map((r) => (
            <a key={r.slug} href={taskHref(r.slug)} className={s.tile}>
              <span className={s.tileTitle}>{r.title}</span>
              <span className={s.grow} />
              <span className={s.tileFoot}>
                <span>{topicNo(r.topic)}</span><span aria-hidden="true">·</span>
                <span className={s.grow}>{r.track ?? r.tier}</span>
                {shared ? null : <span>{r.status}</span>}
                <Icon name="ArrowRight" size={14} />
              </span>
            </a>
          ))}
        </div>
      ) : <EmptyState align="left" message="Nothing yet this week. Whatever you open collects here, passed or not." />}
    </section>
  );
}

/** Today: what to do now, answered before the catalogue. */
export function Today({ data, by, focus, onFocus, onAllDue, tracks, firstRun, onFirstRunDone }: {
  data: Payload; by: Map<string, Row>; focus: string | null;
  onFocus: (tag: string | null) => void; onAllDue: () => void;
  tracks: { name: string; total: number }[]; firstRun: boolean; onFirstRunDone: () => void;
}) {
  const { today, stats } = data;
  const pick = (slugs: string[]) => slugs.map((slug) => by.get(slug)).filter(Boolean) as Row[];
  // reviews first, most overdue first, then the new picks: the order the server sends them
  const queue = pick([...today.review, ...today.new]);
  const head = queue[0];

  // Enter anywhere on the page with nothing focused starts the task Up next
  useEffect(() => {
    if (!head) return;
    const on = (e: KeyboardEvent) => {
      if (e.key !== "Enter" || e.metaKey || e.ctrlKey || e.altKey || e.shiftKey || e.isComposing) return;
      if (document.activeElement && document.activeElement !== document.body) return;
      location.hash = taskHref(head.slug);
    };
    addEventListener("keydown", on);
    return () => removeEventListener("keydown", on);
  }, [head]);

  const stuck = stats.stuck;
  const stuckLine: ReactNode = stuck ? <>You keep struggling with <TagChip label={stuck.tag} small active={focus === stuck.tag}
    onClick={() => onFocus(focus === stuck.tag ? null : stuck.tag)} /> · {stuck.flagged} flagged</> : null;

  return (
    <>
      {firstRun && stats.seen === 0 && today.recent.length === 0 ? (
        <div className="m-drop"><NoticeBanner style={{ background: "var(--surface-2)" }}
          message={<>Every task you pass comes back later than the last time: {inDays(stats.ladder[0])} at
            first, {inDays(stats.ladder.at(-1)!)} once it is solid. A sitting you struggle through brings it
            back sooner instead. Reviews come first and a day holds only so many of them, so a backlog cannot
            bury you. Two new tasks are offered a day whatever the backlog looks like.</>}
          actions={[
            { label: "How it works", onClick: () => window.open(HOW_IT_WORKS, "_blank", "noopener") },
            { label: "Got it", onClick: () => { localStorage.setItem(FIRST_RUN, "1"); onFirstRunDone(); } },
          ]} /></div>
      ) : null}

      <header className={s.head}>
        <div className={s.headText}>
          <span className={s.eyebrow}>{new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" })}</span>
          <h1 className={s.h1}>{headline(today.review.length, today.due_total, today.new.length)}</h1>
          {today.review.length < today.due_total
            ? <p className={s.muted}>{today.review.length} are served a day; the other {today.due_total - today.review.length} stay due.</p> : null}
        </div>
        <dl className={s.stats}>
          <div><dt>done today</dt><dd>{today.done_today}</dd></div>
          <div><dt>practised</dt><dd>{stats.seen}<span> / {stats.total}</span></dd></div>
        </dl>
      </header>

      {/* below 1100px the sidebar is gone, and these chips are where new picks are chosen */}
      <div className={s.rail} role="group" aria-labelledby="rail-h">
        <span id="rail-h" className={s.eyebrow}>New picks from</span>
        {[{ name: "all tracks", key: null as string | null, total: stats.total }, ...tracks.map((r) => ({ ...r, key: r.name }))].map((r) => (
          <TagChip key={r.name} label={`${r.name} · ${r.total}`} active={focus === r.key} onClick={() => onFocus(r.key)} />
        ))}
        {stuckLine ? <span className={s.muted}>{stuckLine}</span> : null}
      </div>

      <div className={s.pair}>
        <UpNext data={data} by={by} queue={queue} focus={focus} onFocus={onFocus} onAllDue={onAllDue} />
        <Ladder stats={stats} />
      </div>

      <Recent rows={pick(today.recent)} window={stats.window} />
    </>
  );
}

export { FIRST_RUN };
