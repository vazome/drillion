import { useCallback, useEffect, useMemo, useState, type CSSProperties, type ReactNode } from "react";
import { Button, Card, EmptyState, Input, LadderMeter, NoticeBanner, Select, StatusBadge, TagChip } from "./ds/index.js";
import { api, post, type Catalogue as Payload, type Row } from "./api";
import { Stats } from "./Stats";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)", whiteSpace: "nowrap" as const };
const FAINT = { fontSize: 12.5, color: "var(--text-faint)", whiteSpace: "nowrap" as const };
const MONO = { fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" as const };
const STATUSES = ["new", "due", "open", "done"];   // api.py _status(): a seen, not-due card is "done"
const DIFFICULTY = ["easy", "medium", "hard"];     // the order the word means, not the alphabet
const DAY = 86400000;
// One column geometry for the header and the rows. The uppercase labels set the widths:
// "DIFFICULTY" plus a sort arrow needs more room than the badge under it does.
const COL = { num: 30, path: 230, difficulty: 104, box: 56, status: 78, reset: 28 };

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;
const num = (topic: number) => String(topic).padStart(3, "0");

/** Today as the server means it: `state.py today()` is `date.today()`, a LOCAL date.
 * en-CA formats it as YYYY-MM-DD, which parses back to the same UTC midnight `due` does. */
const localToday = () => new Date().toLocaleDateString("en-CA");

/** Everything `focus` may name, mirroring `_facets()` in src/drillion/scheduler.py:23 —
 * the tier, the track and the tags alike. The server accepts any of the three, so the
 * catalogue must filter on all three or the screen disagrees with the scheduler. */
const facets = (row: Row) => [row.tier, row.track, ...row.tags];

/** The prereqs a task has not cleared yet — issue #11.
 *
 * Mirrors `unseen()` in src/drillion/scheduler.py: box 1 is the bar, because a first pass
 * graded `struggled` clamps back to box 0 and clears nothing, and under a focus the prereqs
 * outside it are ignored, or a track would stall on a task it does not contain. A card
 * already seen is past the question, so it is never blocked. */
export function blockedBy(row: Row, byTopic: Map<number, Row>, focus: string | null): Row[] {
  if (row.seen) return [];
  return (row.prereqs ?? []).map((t) => byTopic.get(t))
    .filter((p): p is Row => !!p && p.box < 1 && (!focus || facets(p).includes(focus)));
}

/** Why New picks is empty, named rather than guessed — issue #11.
 *
 * `queue()` and `unseen()` (src/drillion/scheduler.py) decide this and keep no reason, so the
 * page re-runs the same rules in the same order over rows it already has: the backlog first,
 * because it holds everything else, then today's cap, then the prereqs, then the focus. The
 * copy this replaced printed all three causes at once and left the reader to guess. */
export function noPicks(all: Row[], blocked: Map<string, Row[]>, focus: string | null,
                        today: Payload["today"]) {
  const unseen = all.filter((r) => !r.seen && r.status !== "open");   // queue() drops open ones
  const inFocus = focus ? unseen.filter((r) => facets(r).includes(focus)) : unseen;
  const ready = inFocus.filter((r) => !blocked.get(r.slug)?.length);
  const link = (r: Row) => <a href={href(r)}>#{num(r.topic)} {r.title}</a>;

  if (today.behind) return {
    why: "behind", act: "backlog" as const,
    message: <>New picks are paused while you catch up — {plural(today.due_total, "review")} waiting,
      and a day holds {today.review.length}. They start again on their own once the backlog is under that.</>,
  };
  if (ready.length) return {
    why: "cap", act: null,
    message: <>That is today's new material — {plural(today.done_today, "new task")} done.
      {" "}{plural(ready.length, "task")} unlocked and waiting for tomorrow.</>,
  };
  if (inFocus.length) {
    // the one closest to opening: fewest unmet prereqs, and the lowest number breaks the tie
    const next = inFocus.reduce((a, b) =>
      (blocked.get(a.slug)?.length ?? 0) <= (blocked.get(b.slug)?.length ?? 0) ? a : b);
    const need = blocked.get(next.slug) ?? [];
    return {
      why: "prereqs", act: null,
      message: <>Every unseen task{focus ? <> under “{focus}”</> : null} is waiting on a prereq.
        The nearest is {link(next)} — pass {need.map((b, i) => <span key={b.slug}>{i ? ", " : ""}{link(b)}</span>)} first.</>,
    };
  }
  if (focus) return {
    why: "focus", act: "focus" as const,
    message: <>Nothing unseen is left under the focus “{focus}” — every task it covers is already started.</>,
  };
  return {
    why: "done", act: null,
    message: <>Nothing unseen is left: you have opened every task in the catalogue. Reviews are the work now.</>,
  };
}

/** "4 days overdue" / "due today" / "due in 3 days" / "never seen". */
function dueText(row: Row) {
  if (!row.seen) return "never seen";
  const days = Math.round((Date.parse(row.due) - Date.parse(localToday())) / DAY);
  if (days === 0) return "due today";
  return days < 0 ? `${plural(-days, "day")} overdue` : `due in ${plural(days, "day")}`;
}

/** D13: a task's tier and its tags read as one filesystem-style path — `core/f-strings · loops`. */
const Path = ({ row }: { row: Row }) => (
  <span title={`${row.tier}/${row.tags.join(" · ")}`} style={{ fontFamily: "var(--font-mono)", fontSize: 12.5, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
    <span style={{ color: "var(--text-faint)" }}>{row.tier}/</span>
    <span style={{ color: "var(--text-muted)" }}>{row.tags.join(" · ")}</span>
  </span>
);

// the API numbers boxes 0-4; the meter fills 1-5, and an unseen card sits on no rung
const rung = (row: Row) => (row.seen ? row.box + 1 : 0);

type SortKey = "topic" | "title" | "path" | "difficulty" | "box" | "status";
type Sort = { key: SortKey; dir: "asc" | "desc" };
const DEFAULT_SORT: Sort = { key: "topic", dir: "asc" };

/** What each column compares on. `difficulty` and `status` rank by the meaning of the word,
 * so hard sorts past medium and the alphabet never gets a say. */
const SORT_ON: Record<SortKey, (row: Row) => string | number> = {
  topic: (r) => r.topic,
  title: (r) => r.title.toLowerCase(),
  path: (r) => `${r.tier}/${r.tags.join(" ")}`,
  difficulty: (r) => DIFFICULTY.indexOf(r.difficulty),
  box: rung,
  status: (r) => STATUSES.indexOf(r.status),
};

/** Sorted rows. Every column but `#` has ties, and rows that reshuffle between renders read
 * as a bug, so the task number breaks them — always ascending, whichever way the column goes. */
export function sortRows(rows: Row[], { key, dir }: Sort): Row[] {
  const on = SORT_ON[key], d = dir === "asc" ? 1 : -1;
  return [...rows].sort((a, b) => {
    const x = on(a), y = on(b);
    const c = typeof x === "number" ? x - (y as number) : String(x).localeCompare(String(y));
    return c ? c * d : a.topic - b.topic;
  });
}

function useHover() {
  const [hover, setHover] = useState(false);
  return [hover, { onMouseEnter: () => setHover(true), onMouseLeave: () => setHover(false) }] as const;
}

const href = (row: Row) => `#/task/${encodeURIComponent(row.slug)}`;

/** A sub-header inside the Today card: what the rows under it are, and one quiet word on why. */
const Band = ({ label, aside, first = false }: { label: string; aside: string; first?: boolean }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 10, padding: first ? "14px 0 8px" : "10px 0 6px", borderTop: first ? "none" : "1px solid var(--border)" }}>
    <span style={LABEL}>{label}</span>
    <span style={FAINT}>{aside}</span>
  </div>
);

/** The two quiet notes a row can carry: what it is waiting for, and whether it keeps beating
 * you. Muted text rather than a badge, deliberately — the lapse flag says "the hints or the
 * prereqs may be the problem, not you", which is worth mentioning and not worth shouting.
 * The prereq numbers are plain text here: the whole row is one anchor already, and an anchor
 * inside an anchor is not valid HTML. The Today card names them as real links instead. */
function Flags({ row, blocked, limit }: { row: Row; blocked: Row[]; limit: number }) {
  const marks: ReactNode[] = [];
  if (blocked.length)
    marks.push(<span key="needs" title={`Not offered as a new pick until these are passed: ${blocked.map((b) => `#${num(b.topic)} ${b.title}`).join(", ")}`}>
      needs {blocked.map((b) => `#${num(b.topic)}`).join(" ")}
    </span>);
  if (row.buried)
    marks.push(<span key="buried" title="Put aside for today. It is back in the queue tomorrow, in the same box and on the same due date — unbury it from the Today panel to have it back sooner.">
      buried today
    </span>);
  if (limit && row.lapses >= limit)
    marks.push(<span key="lapses" title={`You have struggled with this ${row.lapses} times; the hints or the prereqs may be the problem, not you.`}>
      struggled {row.lapses}×
    </span>);
  return marks.length ? <span style={{ ...FAINT, display: "inline-flex", gap: 10 }}>{marks}</span> : null;
}

/** A row of the Today card: when it is due, where it sits on the ladder, and one way in.
 * No status badge — the section it is under already says what it is.
 *
 * `onBury` puts a real button on the row, so the row is a flex box holding the link rather
 * than being the link: an anchor inside an anchor is invalid HTML, and so is a button inside
 * one. Without it the row is exactly what it always was. */
function TodayRow({ row, limit, onBury }: { row: Row; limit: number; onBury?: (buried: boolean) => void }) {
  const [hover, hoverProps] = useHover();
  return (
    <div {...hoverProps}
      style={{ display: "flex", alignItems: "center", borderTop: "1px solid var(--border)", background: hover ? "var(--surface-2)" : "transparent", margin: "0 -18px", padding: "0 18px" }}>
      <a href={href(row)} className="m-tint"
        style={{ display: "flex", alignItems: "center", gap: 14, flex: 1, minWidth: 0, textDecoration: "none", color: "inherit", padding: "9px 0" }}>
        <span style={{ ...FAINT, width: 110, color: "var(--text-muted)" }}>{dueText(row)}</span>
        <LadderMeter box={rung(row)} />
        <span style={{ ...MONO, width: 30, textAlign: "right" }}>{num(row.topic)}</span>
        <span style={{ fontSize: 14.5, fontWeight: 500, flex: 1, display: "flex", alignItems: "baseline", gap: 10 }}>
          {/* nothing in this card is blocked: a new pick is offered only once its prereqs are
            * cleared, and recent work has been seen. Only the lapse flag can show here. */}
          {row.title}<Flags row={row} blocked={[]} limit={limit} />
        </span>
        {/* the whole row is the link; the button is the affordance, so it takes no focus of its own */}
        <span inert aria-hidden="true"><Button variant="secondary" style={{ padding: "6px 12px", fontSize: 13 }}>Open</Button></span>
      </a>
      {onBury ? (
        <Button variant="quiet" onClick={() => onBury(!row.buried)} style={{ fontSize: 13, marginLeft: 12 }}>
          {row.buried ? "Unbury" : "Bury"}
        </Button>
      ) : null}
    </div>
  );
}

/** A row of the list: quiet id, title, the tier/tag path, difficulty, ladder, status.
 * The trailing spacer holds the reset control's column, so the header stays aligned. */
function ListRow({ row, blocked, limit, first = false }: { row: Row; blocked: Row[]; limit: number; first?: boolean }) {
  const [hover, hoverProps] = useHover();
  return (
    <a href={href(row)} className="m-tint" {...hoverProps}
      style={{ display: "flex", alignItems: "center", gap: 14, padding: "0 16px", height: 44, borderTop: first ? "none" : "1px solid var(--border)", textDecoration: "none", color: "inherit", background: hover ? "var(--surface-2)" : "transparent" }}>
      <span style={{ ...MONO, width: COL.num, textAlign: "right" }}>{num(row.topic)}</span>
      <span style={{ flex: 1, display: "flex", alignItems: "baseline", gap: 10, overflow: "hidden" }}>
        <span style={{ fontSize: 15, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{row.title}</span>
        <Flags row={row} blocked={blocked} limit={limit} />
      </span>
      <span style={{ width: COL.path, display: "flex", overflow: "hidden" }}><Path row={row} /></span>
      <span style={{ width: COL.difficulty }}><StatusBadge status={row.difficulty} /></span>
      <span style={{ width: COL.box, height: 16, display: "flex", alignItems: "center" }}><LadderMeter box={rung(row)} /></span>
      <span style={{ width: COL.status }}><StatusBadge status={row.status} /></span>
      <span style={{ width: COL.reset }} />
    </a>
  );
}

/** A column header that sorts, mirroring ds/Table's: hover previews the arrow, the sorted
 * column keeps it in the accent. The list is anchors rather than a `<table>`, so the state
 * goes in the button's own name — `aria-sort` needs table semantics to mean anything. */
function SortHead({ label, col, align, sort, onSort, style }: {
  label: string; col: SortKey; align?: "right"; sort: Sort; onSort: (s: Sort) => void; style: CSSProperties;
}) {
  const [hover, hoverProps] = useHover();
  const active = sort.key === col;
  const next: Sort = { key: col, dir: active && sort.dir === "asc" ? "desc" : "asc" };
  const arrow = active ? (sort.dir === "asc" ? "▲" : "▼") : (hover ? "▲" : "");
  const way = (d: string) => (d === "asc" ? "ascending" : "descending");
  return (
    <button type="button" onClick={() => onSort(next)} {...hoverProps}
      aria-label={active ? `${label}, sorted ${way(sort.dir)}. Sort ${way(next.dir)}` : `Sort by ${label} ${way(next.dir)}`}
      style={{ ...style, display: "inline-flex", alignItems: "center", gap: 5, flexShrink: 0, whiteSpace: "nowrap", justifyContent: align === "right" ? "flex-end" : "flex-start", height: 32, padding: 0, background: "transparent", border: "none", font: "inherit", letterSpacing: "inherit", textTransform: "inherit", color: active || hover ? "var(--text)" : "var(--text-muted)", cursor: "pointer" }}>
      <span>{label}</span>
      <span aria-hidden="true" style={{ fontSize: 8, lineHeight: 1, width: 7, color: active ? "var(--accent)" : "var(--text-faint)" }}>{arrow}</span>
    </button>
  );
}

/** Back to `#` ascending. It sits past Status in the header rather than with the filters,
 * because it undoes the header, not the filtering — and it stays put, greyed, when there is
 * nothing to undo, so the column it occupies never changes width. */
function ResetSort({ disabled, onClick }: { disabled: boolean; onClick: () => void }) {
  const [hover, hoverProps] = useHover();
  return (
    <button type="button" onClick={onClick} disabled={disabled} {...hoverProps}
      title="Reset sort" aria-label="Reset sort to task number, ascending"
      style={{ width: COL.reset, height: 24, display: "inline-flex", alignItems: "center", justifyContent: "center", background: hover && !disabled ? "var(--surface-2)" : "transparent", border: "none", borderRadius: "var(--radius-sm)", fontSize: 15, lineHeight: 1, color: disabled ? "var(--border-strong)" : hover ? "var(--text)" : "var(--text-muted)", cursor: disabled ? "default" : "pointer" }}>
      <span aria-hidden="true">↺</span>
    </button>
  );
}

export function Catalogue() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [activeTags, setActiveTags] = useState<string[]>([]);
  const [notice, setNotice] = useState<string | null>(null);
  const [sort, setSort] = useState<Sort>(DEFAULT_SORT);

  const load = useCallback(() => api<Payload>("/catalogue").then(setData).catch((e) => setError(e.message)), []);
  useEffect(() => { load(); }, [load]);

  const focus = data?.focus ?? null;
  // focus decides what the scheduler may pick next, so the whole payload is stale after it changes
  const setFocus = (tag: string | null) => {
    setNotice(null);
    post("/focus", { tag }).then(load).catch((e) => setNotice(`Focus is still “${focus ?? "any"}” — the change did not save: ${e.message}`));
  };

  // burying moves a card in and out of today's queue, so the queue, the counts and the row
  // all change at once — reload the payload rather than patch three places from one boolean
  const setBuried = (row: Row, buried: boolean) => {
    setNotice(null);
    post(`/task/${encodeURIComponent(row.slug)}/bury`, { buried }).then(load)
      .catch((e) => setNotice(`#${num(row.topic)} ${row.title} is still ${row.buried ? "buried" : "in today’s queue"} — the change did not save: ${e.message}`));
  };

  const by = useMemo(() => new Map((data?.tasks ?? []).map((e) => [e.slug, e])), [data]);
  const byTopic = useMemo(() => new Map((data?.tasks ?? []).map((e) => [e.topic, e])), [data]);
  // what every task is still waiting for, once per payload rather than once per keystroke
  const blocked = useMemo(
    () => new Map((data?.tasks ?? []).map((e) => [e.slug, blockedBy(e, byTopic, focus)])),
    [data, byTopic, focus]);
  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    // `text` is the spec, flattened and lowercased by the server — the same substring
    // contract the title already offered, so every filter still composes with it (#14)
    return (data?.tasks ?? []).filter((e) =>
      (!needle || e.title.toLowerCase().includes(needle) || e.slug.includes(needle)
        || num(e.topic).includes(needle) || !!e.text?.includes(needle)) &&
      (!status || e.status === status) &&
      (!focus || facets(e).includes(focus)) &&
      activeTags.every((t) => e.tags.includes(t)));
  }, [data, q, status, focus, activeTags]);
  const sorted = useMemo(() => sortRows(rows, sort), [rows, sort]);

  if (error) return <EmptyState message={`Could not load the catalogue: ${error}`} />;
  if (!data) return <EmptyState message="Loading…" />;

  const { today, stats } = data;
  const pick = (slugs: string[]) => slugs.map((s) => by.get(s)).filter(Boolean) as Row[];
  const review = pick(today.review), fresh = pick(today.new), recent = pick(today.recent ?? []);   // a server still running last build sends no `recent`
  // every buried card, not just the ones today's panel would have offered: a bury made from
  // the task page has to show up here too, or the only way to see it is the row you left
  const buried = data.tasks.filter((e) => e.buried);
  // ...and a buried card collects there rather than twice: recent activity holds everything
  // worked this week, buried or not, and one card on two rows of one panel is just noise
  const stillOffered = recent.filter((e) => !e.buried);
  const filtered = !!(q || status || activeTags.length || focus);
  const unsorted = sort.key === DEFAULT_SORT.key && sort.dir === DEFAULT_SORT.dir;
  const clear = () => { setQ(""); setStatus(""); setActiveTags([]); if (focus) setFocus(null); };
  // a focus may name a tag, and then that chip is the only thing that explains the filter
  const tagOn = (t: string) => activeTags.includes(t) || focus === t;
  const toggleTag = (t: string) => {
    if (focus === t) return setFocus(null);
    setActiveTags((a) => a.includes(t) ? a.filter((x) => x !== t) : [...a, t]);
  };
  const here = new Set(rows.flatMap((e) => e.tags).concat(activeTags));
  const tagsHere = data.tags.filter((t) => here.has(t));
  // `today.review` is capped, so its length is not the backlog. A cap the page hides reads
  // as "done for today" with ninety cards still waiting, so say both numbers out loud.
  const dueLine = !today.due_total ? "nothing due"
    : review.length < today.due_total ? `showing ${review.length} of ${today.due_total} due`
    : plural(today.due_total, "review");
  const todayLine = [
    dueLine,
    fresh.length ? `${fresh.length} new ${fresh.length === 1 ? "pick" : "picks"}` : null,
    `${today.done_today} done today`,
  ].filter(Boolean).join(" · ");
  // The reason New picks is empty, and the way back out of it — see noPicks().
  const empty = fresh.length ? null : noPicks(data.tasks, blocked, focus, today);
  const act = empty?.act === "backlog" ? { label: "Show the backlog", run: () => setStatus("due") }
    : empty?.act === "focus" ? { label: "Clear focus", run: () => setFocus(null) }
    : null;

  return (
    <div style={{ maxWidth: 1180, margin: "0 auto", display: "grid", gap: 18 }}>
      <Stats boxes={stats.boxes} due={stats.due} seen={stats.seen} total={stats.total} practised={stats.practised} outOf={stats.window} ladderHref="#/progress" />

      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <span style={LABEL}>Today</span>
        <span className="tabular" style={FAINT}>{todayLine}</span>
      </div>

      {notice ? <div className="m-drop"><NoticeBanner message={notice} actions={[{ label: "Dismiss", onClick: () => setNotice(null) }]} /></div> : null}

      <Card padding="0 18px" style={{ overflow: "hidden" }}>
        <div className="m-stagger">
          {/* Recent activity leads, and it is always here: coming back mid-week, the way into
            * what you were last doing beats the queue. The daily cap rations new material and
            * has no say here — this lists as many as the week holds. */}
          <Band label="Recent activity" aside={`last ${stats.window} days`} first />
          {stillOffered.length
            ? stillOffered.map((e) => <TodayRow key={e.slug} row={e} limit={stats.lapse_limit} onBury={(b) => setBuried(e, b)} />)
            : <EmptyState align="left" style={{ padding: "4px 0 10px" }}
                message="Nothing yet this week. Whatever you open collects here, passed or not." />}
          {/* the sub-header carries the focus note, so it stays on screen on an empty day too */}
          <Band label="New picks" aside={today.behind ? "paused — catching up" : focus ? `from ${focus}` : "any"} />
          {fresh.length
            ? fresh.map((e) => <TodayRow key={e.slug} row={e} limit={stats.lapse_limit} onBury={(b) => setBuried(e, b)} />)
            : <EmptyState align="left" style={{ padding: "4px 0 10px" }}
                message={empty!.message} actionLabel={act?.label} onAction={act?.run} />}
          {/* The way to see a bury, and the way out of one before tomorrow takes it. No band
            * on a day with nothing buried: an empty state would describe a control most days
            * never touch. These cards keep their box, their due date and their counts — the
            * only thing a bury changed is that they are not offered until tomorrow. */}
          {buried.length ? <>
            <Band label="Buried" aside="not today — back in the queue tomorrow" />
            {buried.map((e) => <TodayRow key={e.slug} row={e} limit={stats.lapse_limit} onBury={(b) => setBuried(e, b)} />)}
          </> : null}
        </div>
      </Card>

      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 6, flexWrap: "wrap" }}>
        <Input value={q} onChange={setQ} placeholder="search tasks and specs…" ariaLabel="Search tasks by title, number or what the spec says" style={{ width: 260 }} />
        <Select value={status} onChange={setStatus} options={STATUSES} placeholder="any status" ariaLabel="Filter by status" style={{ width: 150 }} />
        <div style={{ width: 1, height: 24, background: "var(--border)" }} />
        {/* a tier or track chip is also the focus: it narrows the list and what the scheduler picks next */}
        {data.tiers.map((t) => <TagChip key={t} label={t} active={focus === t} onClick={() => setFocus(focus === t ? null : t)} />)}
        {data.tracks.length ? <div style={{ width: 1, height: 24, background: "var(--border)" }} /> : null}
        {data.tracks.map((t) => <TagChip key={t} label={t} active={focus === t} onClick={() => setFocus(focus === t ? null : t)} />)}
        <div style={{ flex: 1 }} />
        <span style={FAINT}>{rows.length} of {stats.total} tasks{activeTags.length > 1 ? " · tags matched with AND" : ""}</span>
        {filtered ? <Button variant="quiet" onClick={clear}>Clear</Button> : null}
      </div>
      {/* The map is the vocabulary of what is on screen, wrapped and whole — no scroller.
        * A tag with nothing under the current filter is a dead click, so it drops out; the
        * ones already on stay regardless, or a filter that matched nothing could not be undone. */}
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {tagsHere.map((t) => <TagChip key={t} label={t} active={tagOn(t)} onClick={() => toggleTag(t)} />)}
      </div>

      {/* one flat table: the tier is the first segment of every row's path, so a band
        * header for it was a second copy of the same word and a count nobody reads */}
      <Card padding={0} style={{ overflow: "hidden" }}>
        {sorted.length === 0
          ? <EmptyState message="No task matches those filters. Loosen a tag or clear the search." actionLabel="Clear filters" onAction={clear} />
          : <>
              <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "0 16px", height: 34, borderBottom: "1px solid var(--border-strong)", background: "var(--surface)", ...LABEL }}>
                <SortHead label="#" col="topic" align="right" sort={sort} onSort={setSort} style={{ width: COL.num }} />
                <SortHead label="Task" col="title" sort={sort} onSort={setSort} style={{ flex: 1 }} />
                <SortHead label="tier/tag" col="path" sort={sort} onSort={setSort} style={{ width: COL.path }} />
                <SortHead label="Difficulty" col="difficulty" sort={sort} onSort={setSort} style={{ width: COL.difficulty }} />
                <SortHead label="Box" col="box" sort={sort} onSort={setSort} style={{ width: COL.box }} />
                <SortHead label="Status" col="status" sort={sort} onSort={setSort} style={{ width: COL.status }} />
                <ResetSort disabled={unsorted} onClick={() => setSort(DEFAULT_SORT)} />
              </div>
              {/* no `m-stagger` here: it is an arrival animation, and this list re-orders on every
                * sort and every keystroke in the search box — 171 rows replaying dsRise each time
                * reads as a flicker, not as a list that moved. The Today card keeps it; it arrives once. */}
              <div>{sorted.map((row, i) => <ListRow key={row.slug} row={row} first={i === 0}
                blocked={blocked.get(row.slug) ?? []} limit={stats.lapse_limit} />)}</div>
            </>}
      </Card>
    </div>
  );
}
