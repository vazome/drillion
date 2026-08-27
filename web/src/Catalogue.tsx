import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent } from "react";
import { Band, Button, Card, EmptyState, Input, Kbd, LadderMeter, NoticeBanner, RowFlags, Select, SortReset, StatusBadge, TagChip, TaskPath } from "./ds/index.js";
import { api, post, type Catalogue as Payload, type Row } from "./api";
import { Stats } from "./Stats";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)", whiteSpace: "nowrap" as const };
const FAINT = { fontSize: 12.5, color: "var(--text-faint)", whiteSpace: "nowrap" as const };
const MONO = { fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" as const };
const STATUSES = ["new", "due", "open", "done"];
const DIFFICULTY = ["easy", "medium", "hard"];     // the order the word means, not the alphabet
const DAY = 86400000;
// one column geometry for the header and the rows; the uppercase labels set the widths
const COL = { num: 30, path: 230, difficulty: 104, box: 56, status: 78, reset: 28 };
// below this the list card scrolls sideways rather than squeezing the columns
const LIST_MIN = 840;
const FIRST_RUN = "drillion-first-run";
const HOW_IT_WORKS = "https://github.com/vazome/drillion/blob/main/docs/how-it-works.md";

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;
const num = (topic: number) => String(topic).padStart(3, "0");

/** Today as a LOCAL YYYY-MM-DD, which parses back to the same UTC midnight `due` does. */
const localToday = () => new Date().toLocaleDateString("en-CA");

/** Everything `focus` may name — tier, track and tags alike, as `_facets()` in scheduler.py.
 * All three, or the screen disagrees with the scheduler. */
const facets = (row: Row) => [row.tier, row.track, ...row.tags];

/** The copy for `today.no_new`: the one reason New picks is empty, and the way back out. */
function noPicks(no: NonNullable<Payload["today"]["no_new"]>, today: Payload["today"],
                 focus: string | null, by: Map<string, Row>) {
  const link = (slug: string) => {
    const r = by.get(slug);
    return r ? <a href={href(r)}>#{num(r.topic)} {r.title}</a> : null;
  };
  switch (no.why) {
    case "behind": return {
      act: "backlog" as const,
      message: <>New picks are paused while you catch up — {plural(today.due_total, "review")} waiting,
        and a day holds {today.review.length}. They start again on their own once the backlog is under that.</>,
    };
    case "cap": return {
      act: null,
      message: <>That is today's new material — {plural(today.done_today, "new task")} done.
        {" "}{plural(no.ready, "task")} unlocked and waiting for tomorrow.</>,
    };
    case "prereqs": return {
      act: null,
      message: <>Every unseen task{focus ? <> under “{focus}”</> : null} is waiting on a prereq.
        The nearest is {link(no.nearest)} — pass {(by.get(no.nearest)?.blocked ?? [])
          .map((s, i) => <span key={s}>{i ? ", " : ""}{link(s)}</span>)} first.</>,
    };
    case "focus": return {
      act: "focus" as const,
      message: <>Nothing unseen is left under the focus “{focus}” — every task it covers is already started.</>,
    };
    default: return {
      act: null,
      message: <>Nothing unseen is left: you have opened every task in the catalogue. Reviews are the work now.</>,
    };
  }
}

/** "4 days overdue" / "due today" / "due in 3 days" / "never seen". */
function dueText(row: Row) {
  if (!row.seen) return "never seen";
  const days = Math.round((Date.parse(row.due) - Date.parse(localToday())) / DAY);
  if (days === 0) return "due today";
  return days < 0 ? `${plural(-days, "day")} overdue` : `due in ${plural(days, "day")}`;
}

// the API numbers boxes from 0; the meter fills from 1, and an unseen card sits on no rung
const rung = (row: Row) => (row.seen ? row.box + 1 : 0);

type SortKey = "topic" | "title" | "path" | "difficulty" | "box" | "status";
type Sort = { key: SortKey; dir: "asc" | "desc" };
const DEFAULT_SORT: Sort = { key: "topic", dir: "asc" };

/** What each column compares on; `difficulty` and `status` rank by meaning, not the alphabet. */
const SORT_ON: Record<SortKey, (row: Row) => string | number> = {
  topic: (r) => r.topic,
  title: (r) => r.title.toLowerCase(),
  path: (r) => `${r.tier}/${r.tags.join(" ")}`,
  difficulty: (r) => DIFFICULTY.indexOf(r.difficulty),
  box: rung,
  status: (r) => STATUSES.indexOf(r.status),
};

/** Sorted rows. The task number breaks ties — always ascending, whichever way the column goes. */
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

/** A row of the Today card: when it is due, where it sits on the ladder, and one way in.
 * `onBury` puts a real button on it, so the row holds the link rather than being the link. */
function TodayRow({ row, ladder, limit, onBury }: { row: Row; ladder: number[]; limit: number; onBury?: (buried: boolean) => void }) {
  const [hover, hoverProps] = useHover();
  return (
    <div {...hoverProps}
      style={{ display: "flex", alignItems: "center", borderTop: "1px solid var(--border)", background: hover ? "var(--surface-2)" : "transparent", margin: "0 -18px", padding: "0 18px" }}>
      <a href={href(row)} className="m-tint"
        style={{ display: "flex", alignItems: "center", gap: 14, flex: 1, minWidth: 0, textDecoration: "none", color: "inherit", padding: "9px 0" }}>
        <span style={{ ...FAINT, width: 110, color: "var(--text-muted)" }}>{dueText(row)}</span>
        <LadderMeter box={rung(row)} intervals={ladder} />
        <span style={{ ...MONO, width: 30, textAlign: "right" }}>{num(row.topic)}</span>
        <span style={{ fontSize: 14.5, fontWeight: 500, flex: 1, display: "flex", alignItems: "baseline", gap: 10 }}>
          {/* nothing in this card is blocked: a new pick is offered only once its prereqs clear */}
          {row.title}<RowFlags buried={row.buried} lapses={row.lapses} lapseLimit={limit} />
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

/** A row of the list. The trailing spacer holds the reset control's column, so the header
 * stays aligned. */
function ListRow({ row, blocked, ladder, limit, first = false }: { row: Row; blocked: Row[]; ladder: number[]; limit: number; first?: boolean }) {
  const [hover, hoverProps] = useHover();
  return (
    <a href={href(row)} className="m-tint" {...hoverProps}
      style={{ display: "flex", alignItems: "center", gap: 14, padding: "0 16px", height: 44, minWidth: LIST_MIN, boxSizing: "border-box", borderTop: first ? "none" : "1px solid var(--border)", textDecoration: "none", color: "inherit", background: hover ? "var(--surface-2)" : "transparent" }}>
      <span style={{ ...MONO, width: COL.num, textAlign: "right" }}>{num(row.topic)}</span>
      <span style={{ flex: 1, display: "flex", alignItems: "baseline", gap: 10, overflow: "hidden" }}>
        <span style={{ fontSize: 15, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{row.title}</span>
        <RowFlags needs={blocked} buried={row.buried} lapses={row.lapses} lapseLimit={limit} />
      </span>
      <span style={{ width: COL.path, display: "flex", overflow: "hidden" }}><TaskPath tier={row.tier} tags={row.tags} /></span>
      <span style={{ width: COL.difficulty }}><StatusBadge status={row.difficulty} /></span>
      <span style={{ width: COL.box, height: 16, display: "flex", alignItems: "center" }}><LadderMeter box={rung(row)} intervals={ladder} /></span>
      <span style={{ width: COL.status }}><StatusBadge status={row.status} /></span>
      <span style={{ width: COL.reset }} />
    </a>
  );
}

/** A column header that sorts. The list is anchors rather than a `<table>`, so the state
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

let focusSearchBox: (() => void) | null = null;
let searchWanted = false;

/** `/` from anywhere: focus the catalogue's search box, now or as soon as the page mounts. */
export function focusSearch() {
  if (focusSearchBox) focusSearchBox();
  else searchWanted = true;
}

/** The tag whose tasks keep beating you: the one with the most flagged tasks, at least two. */
function worstTag(rows: Row[], limit: number) {
  if (!limit) return null;
  const flagged = new Map<string, number>(), lapses = new Map<string, number>();
  for (const row of rows) for (const tag of row.tags) {
    lapses.set(tag, (lapses.get(tag) ?? 0) + row.lapses);
    if (row.lapses >= limit) flagged.set(tag, (flagged.get(tag) ?? 0) + 1);
  }
  const worst = [...flagged].filter(([, n]) => n >= 2)
    .sort((a, b) => b[1] - a[1] || (lapses.get(b[0]) ?? 0) - (lapses.get(a[0]) ?? 0) || a[0].localeCompare(b[0]))[0];
  return worst ? { tag: worst[0], flagged: worst[1] } : null;
}

export function Catalogue() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  // `#/?tag=x` is the progress page's way in: read once, then back to a plain `#/` so the
  // header link lights up and a reload or Clear does not bring the filter back
  const [activeTags, setActiveTags] = useState<string[]>(() => new URLSearchParams(location.hash.split("?")[1] ?? "").getAll("tag"));
  useEffect(() => { if (location.hash.includes("?")) location.replace("#/"); }, []);
  const [notice, setNotice] = useState<string | null>(null);
  const [sort, setSort] = useState<Sort>(DEFAULT_SORT);
  const [firstRun, setFirstRun] = useState(() => !localStorage.getItem(FIRST_RUN));
  const searchBox = useRef<HTMLSpanElement>(null);

  const load = useCallback(() => api<Payload>("/catalogue").then(setData).catch((e) => setError(e.message)), []);
  useEffect(() => { load(); }, [load]);

  // the box only exists once the payload has rendered, so a `/` pressed on the task page waits
  const ready = !!data;
  useEffect(() => {
    if (!ready) return;
    focusSearchBox = () => searchBox.current?.querySelector("input")?.focus();
    if (searchWanted) { searchWanted = false; focusSearchBox(); }
    return () => { focusSearchBox = null; };
  }, [ready]);
  // an unconsumed `/` dies with the page, or it steals focus on some later unrelated mount
  useEffect(() => () => { searchWanted = false; }, []);

  const focus = data?.focus ?? null;
  // focus decides what the scheduler may pick next, so the whole payload is stale after it changes
  const setFocus = (tag: string | null) => {
    setNotice(null);
    post("/focus", { tag }).then(load).catch((e) => setNotice(`Focus is still “${focus ?? "any"}” — the change did not save: ${e.message}`));
  };

  // a bury moves the queue, the counts and the row at once — reload rather than patch three
  const setBuried = (row: Row, buried: boolean) => {
    setNotice(null);
    post(`/task/${encodeURIComponent(row.slug)}/bury`, { buried }).then(load)
      .catch((e) => setNotice(`#${num(row.topic)} ${row.title} is still ${row.buried ? "buried" : "in today’s queue"} — the change did not save: ${e.message}`));
  };

  const by = useMemo(() => new Map((data?.tasks ?? []).map((e) => [e.slug, e])), [data]);
  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    // `text` is the spec, already flattened and lowercased by the server
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
  const review = pick(today.review), fresh = pick(today.new), recent = pick(today.recent);
  // every buried card, not just today's: a bury made from the task page shows up here too
  const buried = data.tasks.filter((e) => e.buried);
  // ...and only there: one card on two rows of the same panel is noise
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
  // `today.review` is capped, so its length is not the backlog — say both numbers out loud
  const dueLine = !today.due_total ? "nothing due"
    : review.length < today.due_total ? `showing ${review.length} of ${today.due_total} due`
    : plural(today.due_total, "review");
  const todayLine = [
    dueLine,
    fresh.length ? `${fresh.length} new ${fresh.length === 1 ? "pick" : "picks"}` : null,
    `${today.done_today} done today`,
  ].filter(Boolean).join(" · ");
  // nothing passed and nothing open: the ladder has never shown itself, so say what it is
  const showFirstRun = firstRun && stats.seen === 0 && today.recent.length === 0;
  const dismissFirstRun = () => { localStorage.setItem(FIRST_RUN, "1"); setFirstRun(false); };
  const stuck = worstTag(data.tasks, stats.lapse_limit);
  // Enter in the search box takes the top row of what is on screen — an IME commit is not one
  const onSearchKey = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.nativeEvent.isComposing && sorted.length) location.hash = href(sorted[0]);
  };
  const empty = today.no_new ? noPicks(today.no_new, today, focus, by) : null;
  const act = empty?.act === "backlog" ? { label: "Show the backlog", run: () => setStatus("due") }
    : empty?.act === "focus" ? { label: "Clear focus", run: () => setFocus(null) }
    : null;

  return (
    <div style={{ maxWidth: 1180, margin: "0 auto", display: "grid", gap: 18 }}>
      <Stats boxes={stats.boxes} ladder={stats.ladder} due={stats.due} seen={stats.seen} total={stats.total} practised={stats.practised} outOf={stats.window} ladderHref="#/progress" />

      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <span style={LABEL}>Today</span>
        <span className="tabular" style={FAINT}>{todayLine}</span>
      </div>

      {notice ? <div className="m-drop"><NoticeBanner message={notice} actions={[{ label: "Dismiss", onClick: () => setNotice(null) }]} /></div> : null}

      {/* a welcome, not a warning: NoticeBanner's own `--warn-bg` is what a save failure uses */}
      {showFirstRun ? <div className="m-drop"><NoticeBanner
        style={{ background: "var(--surface-2)" }}
        message={<>Every task you pass climbs a ladder of seven boxes and comes back on that
          box’s own interval — {stats.ladder[0]} days at the first, {stats.ladder.at(-1)} at the
          last — and a sitting you struggle through drops it a box instead. Only two new tasks
          are offered a day. Reviews come first: while the backlog is over the day’s cap, new
          picks pause until you have caught up.</>}
        actions={[
          { label: "How it works", onClick: () => window.open(HOW_IT_WORKS, "_blank", "noopener") },
          { label: "Got it", onClick: dismissFirstRun },
        ]} /></div> : null}

      <Card padding="0 18px" style={{ overflow: "hidden" }}>
        <div className="m-stagger">
          <Band label="Recent activity" aside={`last ${stats.window} days`} first />
          {stillOffered.length
            ? stillOffered.map((e) => <TodayRow key={e.slug} row={e} ladder={stats.ladder} limit={stats.lapse_limit} onBury={(b) => setBuried(e, b)} />)
            : <EmptyState align="left" style={{ padding: "4px 0 10px" }}
                message="Nothing yet this week. Whatever you open collects here, passed or not." />}
          <Band label="New picks" aside={today.behind ? "paused — catching up" : focus ? `from ${focus}` : "any"} />
          {fresh.length
            ? fresh.map((e) => <TodayRow key={e.slug} row={e} ladder={stats.ladder} limit={stats.lapse_limit} onBury={(b) => setBuried(e, b)} />)
            : <EmptyState align="left" style={{ padding: "4px 0 10px" }}
                message={empty!.message} actionLabel={act?.label} onAction={act?.run} />}
          {buried.length ? <>
            <Band label="Buried" aside="not today — back in the queue tomorrow" />
            {buried.map((e) => <TodayRow key={e.slug} row={e} ladder={stats.ladder} limit={stats.lapse_limit} onBury={(b) => setBuried(e, b)} />)}
          </> : null}
          {stuck ? <>
            <Band label="Worth a focus" />
            <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", fontSize: 14, padding: "0 0 12px" }}>
              <span>You keep struggling with</span>
              <TagChip label={stuck.tag} active={focus === stuck.tag} onClick={() => setFocus(focus === stuck.tag ? null : stuck.tag)} />
              {/* the chip clears the focus once it is on, so the offer to set it goes away */}
              <span>— {plural(stuck.flagged, "task")} are flagged.
                {focus === stuck.tag ? null : " Focusing on it puts its unstarted tasks first."}</span>
            </div>
          </> : null}
        </div>
      </Card>

      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 6, flexWrap: "wrap" }}>
        <span ref={searchBox} onKeyDown={onSearchKey} style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
          <Input value={q} onChange={setQ} placeholder="search tasks and specs…" ariaLabel="Search tasks by title, number or what the spec says — Enter opens the first match" style={{ width: 260 }} />
          <Kbd>/</Kbd>
        </span>
        <Select value={status} onChange={setStatus} options={STATUSES} placeholder="any status" ariaLabel="Filter by status" style={{ width: 150 }} />
        <div style={{ width: 1, height: 24, background: "var(--border)" }} />
        {data.tiers.map((t) => <TagChip key={t} label={t} active={focus === t} onClick={() => setFocus(focus === t ? null : t)} />)}
        {data.tracks.length ? <div style={{ width: 1, height: 24, background: "var(--border)" }} /> : null}
        {data.tracks.map((t) => <TagChip key={t} label={t} active={focus === t} onClick={() => setFocus(focus === t ? null : t)} />)}
        <div style={{ flex: 1 }} />
        <span style={FAINT}>{rows.length} of {stats.total} tasks{activeTags.length > 1 ? " · tags matched with AND" : ""}</span>
        {filtered ? <Button variant="quiet" onClick={clear}>Clear</Button> : null}
      </div>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {tagsHere.map((t) => <TagChip key={t} label={t} active={tagOn(t)} onClick={() => toggleTag(t)} />)}
      </div>

      {/* narrower than the columns need, the card scrolls sideways; the page body never does */}
      <Card padding={0} style={{ overflowX: "auto" }}>
        {sorted.length === 0
          ? <EmptyState message="No task matches those filters. Loosen a tag or clear the search." actionLabel="Clear filters" onAction={clear} />
          : <>
              <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "0 16px", height: 34, minWidth: LIST_MIN, boxSizing: "border-box", borderBottom: "1px solid var(--border-strong)", background: "var(--surface)", ...LABEL }}>
                <SortHead label="#" col="topic" align="right" sort={sort} onSort={setSort} style={{ width: COL.num }} />
                <SortHead label="Task" col="title" sort={sort} onSort={setSort} style={{ flex: 1 }} />
                <SortHead label="tier/tag" col="path" sort={sort} onSort={setSort} style={{ width: COL.path }} />
                <SortHead label="Difficulty" col="difficulty" sort={sort} onSort={setSort} style={{ width: COL.difficulty }} />
                <SortHead label="Box" col="box" sort={sort} onSort={setSort} style={{ width: COL.box }} />
                <SortHead label="Status" col="status" sort={sort} onSort={setSort} style={{ width: COL.status }} />
                <SortReset disabled={unsorted} onClick={() => setSort(DEFAULT_SORT)} style={{ width: COL.reset }} />
              </div>
              <div style={{ minWidth: LIST_MIN }}>{sorted.map((row, i) => <ListRow key={row.slug} row={row} first={i === 0}
                blocked={pick(row.blocked ?? [])} ladder={stats.ladder} limit={stats.lapse_limit} />)}</div>
            </>}
      </Card>
    </div>
  );
}
