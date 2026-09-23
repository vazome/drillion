import { useCallback, useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { Button, EmptyState, Icon, Input, Kbd, NoticeBanner, RowFlags, SortReset, TagChip, TaskPath } from "./ds/index.js";
import { api, FOCUS_SAVED, setFocus as saveFocus, type Catalogue as Payload, type Row } from "./api";
import { FIRST_RUN, Today } from "./Today";
import { Level } from "./Level";
import css from "./Catalogue.module.css";
import { strength } from "./strength";
import { depsHref, taskHref } from "./Deps";
import { topicNo } from "./format";

const STATUSES = ["new", "due", "open", "done"] as const;
const DIFFICULTY = ["easy", "medium", "hard"];     // the order the word means, not the alphabet

/** Everything `focus` may name — tier, track and tags alike, as `_facets()` in scheduler.py.
 * All three, or the screen disagrees with the scheduler. */
const facets = (row: Row) => [row.tier, row.track, ...row.tags].filter(Boolean) as string[];

type SortKey = "topic" | "title" | "path" | "difficulty" | "strength" | "status";
type Sort = { key: SortKey; dir: "asc" | "desc" };
const DEFAULT_SORT: Sort = { key: "topic", dir: "asc" };

/** What each column compares on; `difficulty` and `status` rank by meaning, not the alphabet. */
const SORT_ON: Record<SortKey, (row: Row) => string | number> = {
  topic: (r) => r.topic,
  title: (r) => r.title.toLowerCase(),
  path: (r) => `${r.tier}/${r.tags.join(" ")}`,
  difficulty: (r) => DIFFICULTY.indexOf(r.difficulty),
  // an unpractised task sorts below every practised one, whichever way the column goes
  strength: (r) => (r.seen ? r.box + 1 : 0),
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

const href = (row: Row) => taskHref(row.slug);

/** A row of the list: one line, the path in its own column, and `needs 289` in words. */
function ListRow({ row, blocked, ladder, limit, next }: { row: Row; blocked: Row[]; ladder: number[]; limit: number; next: boolean }) {
  const known = strength(row.box, !!row.seen, ladder);
  return (
    <a href={href(row)} className={`m-tint ${css.row}`}>
      <span className={css.num}>{topicNo(row.topic)}</span>
      <span className={css.task}>
        <span className={css.title}>{row.title}</span>
        {next ? <span className={css.next}>up next</span> : null}
        {/* the flag is the second way into the lineage; the rest of the row still opens the task */}
        <RowFlags needs={blocked} onNeedsClick={() => { location.hash = depsHref(row.slug); }}
          lapses={row.lapses} lapseLimit={limit} />
      </span>
      <span className={css.cell}><TaskPath tier={row.tier} track={row.track} tags={row.tags} /></span>
      <span><Level of={row.difficulty} /></span>
      {/* an unpractised task already says NEW under Status; a second word saying so is noise */}
      <span>{known ? <Level of={known} /> : null}</span>
      <span className={css.status}>{row.status}</span>
      <span />
    </a>
  );
}

/** A column header that sorts. The list is anchors rather than a `<table>`, so the state
 * goes in the button's own name — `aria-sort` needs table semantics to mean anything. */
function SortHead({ label, col, sort, onSort }: { label: string; col: SortKey; sort: Sort; onSort: (s: Sort) => void }) {
  const active = sort.key === col;
  const next: Sort = { key: col, dir: active && sort.dir === "asc" ? "desc" : "asc" };
  // an inactive column's arrow is always drawn, and shown only under the pointer
  const arrow = active && sort.dir === "desc" ? "ArrowDown" : "ArrowUp";
  const way = (d: string) => (d === "asc" ? "ascending" : "descending");
  return (
    <button type="button" onClick={() => onSort(next)} className={css.sort} data-active={active || undefined}
      aria-label={active ? `${label}, sorted ${way(sort.dir)}. Sort ${way(next.dir)}` : `Sort by ${label} ${way(next.dir)}`}>
      <span>{label}</span>
      <span aria-hidden="true" className={css.arrow}><Icon name={arrow} size={12} /></span>
    </button>
  );
}

/** The query of `#/?…`, the page's one inbox: `q` from the `/` key, `tag` from a progress link. */
const inbox = () => new URLSearchParams(location.hash.split("?")[1] ?? "");

export function Catalogue() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [activeTags, setActiveTags] = useState<string[]>(() => inbox().getAll("tag"));
  const [notice, setNotice] = useState<string | null>(null);
  const [sort, setSort] = useState<Sort>(DEFAULT_SORT);
  const [firstRun, setFirstRun] = useState(() => !localStorage.getItem(FIRST_RUN));
  const searchBox = useRef<HTMLSpanElement>(null);
  const listHead = useRef<HTMLDivElement>(null);
  const wantSearch = useRef(inbox().has("q"));

  const load = useCallback(() => api<Payload>("/catalogue").then(setData).catch((e) => setError(e.message)), []);
  useEffect(() => {
    load();
    addEventListener(FOCUS_SAVED, load);
    return () => removeEventListener(FOCUS_SAVED, load);
  }, [load]);

  // the box exists only once the payload has rendered, so a `/` from another route waits
  const focusSearch = () => {
    const box = searchBox.current?.querySelector("input");
    if (box) { wantSearch.current = false; box.focus(); }
  };

  // the mount read the hash above; this is the same inbox arriving while the page is up
  useEffect(() => {
    const take = () => {
      if (!location.hash.includes("?")) return;
      const params = inbox();
      const tags = params.getAll("tag");
      if (tags.length) setActiveTags(tags);
      if (params.has("q")) wantSearch.current = true;
      location.replace("#/");
      focusSearch();
    };
    addEventListener("hashchange", take);
    return () => removeEventListener("hashchange", take);
  }, []);

  // emptying the hash keeps the header link lit and stops a reload replaying the query
  const ready = !!data || !!error;
  useEffect(() => {
    if (location.hash.includes("?")) location.replace("#/");
    if (ready && wantSearch.current) focusSearch();
  }, [ready]);

  const focus = data?.focus ?? null;
  // focus decides what the scheduler may pick next, so the whole payload is stale after it changes
  const setFocus = (tag: string | null) => {
    setNotice(null);
    saveFocus(tag).catch((e) => setNotice(`Focus is still “${focus ?? "any"}” — the change did not save: ${e.message}`));
  };

  const by = useMemo(() => new Map((data?.tasks ?? []).map((e) => [e.slug, e])), [data]);
  // every filter but status, so the status toggle can count what each choice would show
  const matching = useMemo(() => {
    const needle = q.trim().toLowerCase();
    // `text` is the spec, already flattened and lowercased by the server
    return (data?.tasks ?? []).filter((e) =>
      (!needle || e.title.toLowerCase().includes(needle) || e.slug.includes(needle)
        || topicNo(e.topic).includes(needle) || e.text.includes(needle) || e.tags.some((t) => t.includes(needle))) &&
      (!focus || facets(e).includes(focus)) &&
      activeTags.every((t) => e.tags.includes(t)));
  }, [data, q, focus, activeTags]);
  const counts = useMemo(() => Object.fromEntries(STATUSES.map((k) => [k, matching.filter((e) => e.status === k).length])), [matching]);
  const rows = useMemo(() => matching.filter((e) => !status || e.status === status), [matching, status]);
  const sorted = useMemo(() => sortRows(rows, sort), [rows, sort]);

  if (error) return <EmptyState message={`Could not load the catalogue: ${error}`} />;
  if (!data) return <EmptyState message="Loading…" />;

  const { today, stats } = data;
  const pick = (slugs: string[]) => slugs.map((s) => by.get(s)).filter(Boolean) as Row[];
  const head = today.review[0] ?? today.new[0];
  const filtered = !!(q || status || activeTags.length);
  const unsorted = sort.key === DEFAULT_SORT.key && sort.dir === DEFAULT_SORT.dir;
  const clear = () => { setQ(""); setStatus(""); setActiveTags([]); };
  // a focus may name a tag, and then that chip is the only thing that explains the filter
  const tagOn = (t: string) => activeTags.includes(t) || focus === t;
  const toggleTag = (t: string) => {
    if (focus === t) return setFocus(null);
    setActiveTags((a) => a.includes(t) ? a.filter((x) => x !== t) : [...a, t]);
  };
  const here = new Set(rows.flatMap((e) => e.tags).concat(activeTags));
  const tagsHere = data.tags.filter((t) => here.has(t));
  const tiersHere = rows.some((e) => e.tier) || data.tiers.includes(focus ?? "");
  // Enter in the search box takes the top row of what is on screen — an IME commit is not one
  const onSearchKey = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.nativeEvent.isComposing && sorted.length) location.hash = href(sorted[0]);
  };
  const tracks = data.tracks.map((name) => ({ name, total: data.tasks.filter((e) => e.track === name).length }));
  const allDue = () => {
    setStatus("due");
    listHead.current?.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  };

  return (
    <div className={css.page}>
      {notice ? <div className="m-drop"><NoticeBanner message={notice} actions={[{ label: "Dismiss", onClick: () => setNotice(null) }]} /></div> : null}
      <Today data={data} by={by} focus={focus} onFocus={setFocus} onAllDue={allDue} tracks={tracks}
        firstRun={firstRun} onFirstRunDone={() => setFirstRun(false)} />

      <section aria-labelledby="cat-h" className={css.section}>
        <div ref={listHead} className={css.heading}>
          <h2 id="cat-h" className={css.h2}>Catalogue</h2>
          {focus ? (
            <span className={css.focus}>{focus} · {rows.length} of {stats.total}
              <button type="button" onClick={() => setFocus(null)} aria-label={`Clear the focus on ${focus} and show every track`}><Icon name="Close" size={12} /></button>
            </span>
          ) : filtered ? <span className={css.count}>{rows.length} of {stats.total} tasks{activeTags.length > 1 ? " · tags matched with AND" : ""}</span> : null}
          {filtered ? <Button variant="quiet" onClick={clear}>Clear</Button> : null}
          <span className={css.grow} />
          <span ref={searchBox} onKeyDown={onSearchKey} className={css.search}>
            <Icon name="Search" className={css.searchIcon} />
            <Input value={q} onChange={setQ} placeholder="Search titles, specs and tags" ariaLabel="Search tasks by title, number or what the spec says — Enter opens the first match" style={{ width: "100%", paddingLeft: 34, paddingRight: 36 }} />
            <Kbd className={css.slash}>/</Kbd>
          </span>
        </div>

        <div className={css.filters}>
          <div role="group" aria-label="Status" className={css.segment}>
            <button type="button" aria-pressed={!status} onClick={() => setStatus("")}>Any</button>
            {STATUSES.map((k) => (
              <button key={k} type="button" aria-pressed={status === k} onClick={() => setStatus(status === k ? "" : k)}>
                {k} <span className={css.segCount}>{counts[k]}</span>
              </button>
            ))}
          </div>
          <div className={css.tags}>
            {/* a tier is Python depth, so its chips go when nothing listed is Python; a tier that
              * is the focus stays, since its chip is the way back out */}
            {tiersHere ? <>
              <span className={css.count}>python</span>
              {data.tiers.map((t) => <TagChip key={t} label={t} active={focus === t} onClick={() => setFocus(focus === t ? null : t)} />)}
              <span className={css.rule} />
            </> : null}
            {tagsHere.map((t) => <TagChip key={t} label={t} active={tagOn(t)} onClick={() => toggleTag(t)} />)}
          </div>
        </div>

        {/* narrower than the columns need, the card scrolls sideways; the page body never does */}
        <div className={css.list}>
          {sorted.length === 0
            ? <EmptyState message="No task matches those filters. Loosen a tag or clear the search." actionLabel="Clear filters" onAction={() => { clear(); if (focus) setFocus(null); }} />
            : <>
                <div className={css.header}>
                  <SortHead label="#" col="topic" sort={sort} onSort={setSort} />
                  <SortHead label="Task" col="title" sort={sort} onSort={setSort} />
                  <SortHead label="Path" col="path" sort={sort} onSort={setSort} />
                  <SortHead label="Difficulty" col="difficulty" sort={sort} onSort={setSort} />
                  <SortHead label="Known" col="strength" sort={sort} onSort={setSort} />
                  <SortHead label="Status" col="status" sort={sort} onSort={setSort} />
                  <SortReset disabled={unsorted} onClick={() => setSort(DEFAULT_SORT)} />
                </div>
                {sorted.map((row) => <ListRow key={row.slug} row={row} next={row.slug === head}
                  blocked={pick(row.blocked)} ladder={stats.ladder} limit={stats.lapse_limit} />)}
              </>}
        </div>
      </section>
    </div>
  );
}
