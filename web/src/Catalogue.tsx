import { useCallback, useEffect, useMemo, useState, type CSSProperties } from "react";
import { Button, Card, EmptyState, Input, LadderMeter, NoticeBanner, Select, StatusBadge, TagChip } from "./ds/index.js";
import { api, post, type Catalogue as Payload, type Row } from "./api";
import { Stats } from "./Stats";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)", whiteSpace: "nowrap" as const };
const FAINT = { fontSize: 12.5, color: "var(--text-faint)", whiteSpace: "nowrap" as const };
const MONO = { fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" as const };
const STATUSES = ["new", "due", "open", "done"];   // api.py _status(): a seen, not-due card is "done"
const DIFFICULTY = ["easy", "medium", "hard"];     // the order the word means, not the alphabet
const DAY = 86400000;

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

/** Today as the server means it: `state.py today()` is `date.today()`, a LOCAL date.
 * en-CA formats it as YYYY-MM-DD, which parses back to the same UTC midnight `due` does. */
const localToday = () => new Date().toLocaleDateString("en-CA");

/** Everything `focus` may name, mirroring `_facets()` in src/drillion/scheduler.py:23 —
 * the tier, the track and the tags alike. The server accepts any of the three, so the
 * catalogue must filter on all three or the screen disagrees with the scheduler. */
const facets = (row: Row) => [row.tier, row.track, ...row.tags];

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

/** A row of the Today card: what it is, when it was due, and one way in. */
function TodayRow({ row, first = false }: { row: Row; first?: boolean }) {
  const [hover, hoverProps] = useHover();
  return (
    <a href={href(row)} className="m-tint" {...hoverProps}
      style={{ display: "flex", alignItems: "center", gap: 14, textDecoration: "none", color: "inherit", borderTop: first ? "none" : "1px solid var(--border)", background: hover ? "var(--surface-2)" : "transparent", margin: "0 -18px", padding: "9px 18px" }}>
      <StatusBadge status={row.status} />
      <span style={{ ...FAINT, width: 96, color: "var(--text-muted)" }}>{dueText(row)}</span>
      <LadderMeter box={rung(row)} />
      <span style={{ ...MONO, width: 30, textAlign: "right" }}>{String(row.topic).padStart(3, "0")}</span>
      <span style={{ fontSize: 14.5, fontWeight: 500, flex: 1 }}>{row.title}</span>
      {/* the whole row is the link; the button is the affordance, so it takes no focus of its own */}
      <span inert aria-hidden="true"><Button variant="secondary" style={{ padding: "6px 12px", fontSize: 13 }}>Open</Button></span>
    </a>
  );
}

/** A row of a tier group: quiet id, title, the tier/tag path, difficulty, ladder, status. */
function ListRow({ row }: { row: Row }) {
  const [hover, hoverProps] = useHover();
  return (
    <a href={href(row)} className="m-tint" {...hoverProps}
      style={{ display: "flex", alignItems: "center", gap: 14, padding: "0 16px", height: 44, borderTop: "1px solid var(--border)", textDecoration: "none", color: "inherit", background: hover ? "var(--surface-2)" : "transparent" }}>
      <span style={{ ...MONO, width: 30, textAlign: "right" }}>{String(row.topic).padStart(3, "0")}</span>
      <span style={{ fontSize: 15, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{row.title}</span>
      <span style={{ width: 230, display: "flex", overflow: "hidden" }}><Path row={row} /></span>
      <span style={{ width: 74 }}><StatusBadge status={row.difficulty} /></span>
      <span style={{ width: 52, height: 16, display: "flex", alignItems: "center" }}><LadderMeter box={rung(row)} /></span>
      <span style={{ width: 74 }}><StatusBadge status={row.status} /></span>
    </a>
  );
}

/** One tier as a band inside the list: a name, a count, and its rows. Not collapsible —
 * the tier is already on every row as the first segment of the path. */
function TierGroup({ tier, rows, first }: { tier: string; rows: Row[]; first: boolean }) {
  return (
    <>
      <div style={{ display: "flex", alignItems: "center", gap: 10, height: 34, padding: "0 16px", background: "var(--surface-2)", borderTop: first ? "none" : "1px solid var(--border-strong)", fontSize: 13.5, fontWeight: 600, color: "var(--text)" }}>
        <span>{tier}</span>
        <span style={MONO}>({rows.length})</span>
      </div>
      <div className="m-stagger">{rows.map((row) => <ListRow key={row.slug} row={row} />)}</div>
    </>
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
      style={{ ...style, display: "inline-flex", alignItems: "center", gap: 5, justifyContent: align === "right" ? "flex-end" : "flex-start", height: 32, padding: 0, background: "transparent", border: "none", font: "inherit", letterSpacing: "inherit", textTransform: "inherit", color: active || hover ? "var(--text)" : "var(--text-muted)", cursor: "pointer" }}>
      <span>{label}</span>
      <span aria-hidden="true" style={{ fontSize: 8, lineHeight: 1, width: 7, color: active ? "var(--accent)" : "var(--text-faint)" }}>{arrow}</span>
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

  const by = useMemo(() => new Map((data?.tasks ?? []).map((e) => [e.slug, e])), [data]);
  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return (data?.tasks ?? []).filter((e) =>
      (!needle || e.title.toLowerCase().includes(needle) || e.slug.includes(needle) || String(e.topic).padStart(3, "0").includes(needle)) &&
      (!status || e.status === status) &&
      (!focus || facets(e).includes(focus)) &&
      activeTags.every((t) => e.tags.includes(t)));
  }, [data, q, status, focus, activeTags]);
  const sorted = useMemo(() => sortRows(rows, sort), [rows, sort]);

  if (error) return <EmptyState message={`Could not load the catalogue: ${error}`} />;
  if (!data) return <EmptyState message="Loading…" />;

  const { today, stats } = data;
  const pick = (slugs: string[]) => slugs.map((s) => by.get(s)).filter(Boolean) as Row[];
  const review = pick(today.review), fresh = pick(today.new);
  const filtered = !!(q || status || activeTags.length || focus);
  const unsorted = sort.key === DEFAULT_SORT.key && sort.dir === DEFAULT_SORT.dir;
  const clear = () => { setQ(""); setStatus(""); setActiveTags([]); if (focus) setFocus(null); };
  // a focus may name a tag, and then that chip is the only thing that explains the filter
  const tagOn = (t: string) => activeTags.includes(t) || focus === t;
  const toggleTag = (t: string) => {
    if (focus === t) return setFocus(null);
    setActiveTags((a) => a.includes(t) ? a.filter((x) => x !== t) : [...a, t]);
  };
  const todayLine = [
    review.length ? plural(review.length, "review") : "nothing due",
    fresh.length ? `${fresh.length} new ${fresh.length === 1 ? "pick" : "picks"}` : null,
    `${today.done_today} done today`,
  ].filter(Boolean).join(" · ");

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
          {review.map((e, i) => <TodayRow key={e.slug} row={e} first={i === 0} />)}
          {/* the sub-header carries the focus note, so it stays on screen on an empty day too */}
          <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 0 6px", borderTop: "1px solid var(--border)" }}>
            <span style={LABEL}>New picks</span>
            <span style={FAINT}>{focus ? `from ${focus}` : "any"}</span>
          </div>
          {/* Three things empty this list — the daily cap, an unmet prereq and the focus — and
            * the payload cannot tell them apart, so the copy names all three rather than
            * blaming the cap for a day the prereqs closed off. */}
          {fresh.length
            ? fresh.map((e) => <TodayRow key={e.slug} row={e} />)
            : <EmptyState align="left" style={{ padding: "4px 0 10px" }}
                message={review.length ? "No new picks right now — today's cap, an unmet prereq, or the focus. Finish the reviews above, or rest."
                                       : "Nothing due, and no new pick unlocked — today's cap, an unmet prereq, or the focus. Pick anything below, or rest."} />}
        </div>
      </Card>

      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 6, flexWrap: "wrap" }}>
        <Input value={q} onChange={setQ} placeholder="search title or topic…" ariaLabel="Search tasks by title or topic" style={{ width: 260 }} />
        <Select value={status} onChange={setStatus} options={STATUSES} placeholder="any status" ariaLabel="Filter by status" style={{ width: 150 }} />
        <div style={{ width: 1, height: 24, background: "var(--border)" }} />
        {/* a tier or track chip is also the focus: it narrows the list and what the scheduler picks next */}
        {data.tiers.map((t) => <TagChip key={t} label={t} active={focus === t} onClick={() => setFocus(focus === t ? null : t)} />)}
        {data.tracks.length ? <div style={{ width: 1, height: 24, background: "var(--border)" }} /> : null}
        {data.tracks.map((t) => <TagChip key={t} label={t} active={focus === t} onClick={() => setFocus(focus === t ? null : t)} />)}
        <div style={{ flex: 1 }} />
        <span style={FAINT}>{rows.length} of {stats.total} tasks{activeTags.length > 1 ? " · tags matched with AND" : ""}</span>
        {unsorted ? null : <Button variant="secondary" onClick={() => setSort(DEFAULT_SORT)} style={{ padding: "6px 10px", fontSize: 13, fontWeight: 500, color: "var(--text-muted)" }}>↺ Reset sort</Button>}
        {filtered ? <Button variant="quiet" onClick={clear}>Clear</Button> : null}
      </div>
      {/* every tag, wrapped and whole: a scroller hid two thirds of the map and moved the
        * chip you just clicked, and the map is the one place the vocabulary is visible. */}
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {data.tags.map((t) => <TagChip key={t} label={t} active={tagOn(t)} onClick={() => toggleTag(t)} />)}
      </div>

      {/* one table: the tiers are bands inside it, not three cards */}
      <Card padding={0} style={{ overflow: "hidden" }}>
        {sorted.length === 0
          ? <EmptyState message="No task matches those filters. Loosen a tag or clear the search." actionLabel="Clear filters" onAction={clear} />
          : <>
              <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "0 16px", height: 32, borderBottom: "1px solid var(--border-strong)", background: "var(--surface)", ...LABEL }}>
                <SortHead label="#" col="topic" align="right" sort={sort} onSort={setSort} style={{ width: 30 }} />
                <SortHead label="Task" col="title" sort={sort} onSort={setSort} style={{ flex: 1 }} />
                <SortHead label="tier/tag" col="path" sort={sort} onSort={setSort} style={{ width: 230 }} />
                <SortHead label="Difficulty" col="difficulty" sort={sort} onSort={setSort} style={{ width: 74 }} />
                <SortHead label="Box" col="box" sort={sort} onSort={setSort} style={{ width: 52 }} />
                <SortHead label="Status" col="status" sort={sort} onSort={setSort} style={{ width: 74 }} />
              </div>
              {data.tiers.map((tier, i) => {
                const group = sorted.filter((e) => e.tier === tier);
                return group.length ? <TierGroup key={tier} tier={tier} rows={group} first={i === 0} /> : null;
              })}
            </>}
      </Card>
    </div>
  );
}
