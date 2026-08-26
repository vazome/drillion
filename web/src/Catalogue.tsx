import { useCallback, useEffect, useMemo, useState } from "react";
import { Button, Card, EmptyState, Input, LadderMeter, Select, StatusBadge, TagChip } from "./ds/index.js";
import { api, post, type Catalogue as Payload, type Row } from "./api";
import { Stats } from "./Stats";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)", whiteSpace: "nowrap" as const };
const FAINT = { fontSize: 12.5, color: "var(--text-faint)", whiteSpace: "nowrap" as const };
const MONO = { fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-faint)", fontVariantNumeric: "tabular-nums" as const };
const STATUSES = ["new", "due", "scheduled", "open", "done"];
const OPEN_KEY = "drillion-catalogue-open";   // which tier groups the reader left open
const DAY = 86400000;

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

/** "4 days overdue" / "due today" / "due in 3 days" / "never seen". */
function dueText(row: Row) {
  if (!row.seen) return "never seen";
  const days = Math.round((Date.parse(row.due) - Date.parse(new Date().toISOString().slice(0, 10))) / DAY);
  if (days === 0) return "due today";
  return days < 0 ? `${plural(-days, "day")} overdue` : `due in ${plural(days, "day")}`;
}

/** D13: a task's tier and its tags read as one filesystem-style path — `core/f-strings · loops`. */
const Path = ({ row }: { row: Row }) => (
  <span title={`${row.tier}/${row.tags.join(" ")}`} style={{ fontFamily: "var(--font-mono)", fontSize: 12.5, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
    <span style={{ color: "var(--text-faint)" }}>{row.tier}/</span>
    <span style={{ color: "var(--text-muted)" }}>{row.tags.join(" · ")}</span>
  </span>
);

// the API numbers boxes 0-4; the meter fills 1-5, and an unseen card sits on no rung
const rung = (row: Row) => (row.seen ? row.box + 1 : 0);

function useHover() {
  const [hover, setHover] = useState(false);
  return [hover, { onMouseEnter: () => setHover(true), onMouseLeave: () => setHover(false) }] as const;
}

const href = (row: Row) => `#/task/${encodeURIComponent(row.slug)}`;

/** A row of the Today card: what it is, when it was due, and one way in. */
function TodayRow({ row }: { row: Row }) {
  const [hover, hoverProps] = useHover();
  return (
    <a href={href(row)} className="m-tint" {...hoverProps}
      style={{ display: "flex", alignItems: "center", gap: 14, padding: "9px 0", textDecoration: "none", color: "inherit", borderTop: "1px solid var(--border)", opacity: hover ? 0.86 : 1 }}>
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

/** One tier, collapsed to its name and count until asked. */
function TierGroup({ tier, rows, open, onToggle }: { tier: string; rows: Row[]; open: boolean; onToggle: () => void }) {
  const [hover, hoverProps] = useHover();
  return (
    <Card padding={0} style={{ overflow: "hidden" }}>
      <button type="button" aria-expanded={open} onClick={onToggle} {...hoverProps} className="m-tint"
        style={{ display: "flex", alignItems: "center", gap: 10, width: "100%", height: 40, padding: "0 16px", background: hover ? "var(--surface-2)" : "transparent", border: "none", cursor: "pointer", fontFamily: "var(--font-sans)", fontSize: 13.5, fontWeight: 600, color: "var(--text)", textAlign: "left" }}>
        <span aria-hidden="true" style={{ width: 9, fontSize: 11, color: "var(--text-muted)", display: "inline-block", transform: open ? "rotate(90deg)" : "none", transition: "transform var(--dur-base) var(--ease-out)" }}>▸</span>
        <span>{tier}</span>
        <span style={MONO}>({rows.length})</span>
      </button>
      {open ? (
        <div className="m-stagger">
          <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "0 16px", height: 32, borderTop: "1px solid var(--border)", ...LABEL }}>
            <span style={{ width: 30, textAlign: "right" }}>#</span>
            <span style={{ flex: 1 }}>Task</span>
            <span style={{ width: 230 }}>tier/tag</span>
            <span style={{ width: 74 }}>Difficulty</span>
            <span style={{ width: 52 }}>Box</span>
            <span style={{ width: 74 }}>Status</span>
          </div>
          {rows.map((row) => <ListRow key={row.slug} row={row} />)}
        </div>
      ) : null}
    </Card>
  );
}

export function Catalogue({ onHead }: { onHead: (h: { total: number; daysLeft: number }) => void }) {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [activeTags, setActiveTags] = useState<string[]>([]);
  const [openTiers, setOpenTiers] = useState<Record<string, boolean>>(() => {
    try { return JSON.parse(localStorage.getItem(OPEN_KEY) || "{}"); } catch { return {}; }
  });

  const load = useCallback(() => api<Payload>("/catalogue").then((d) => {
    setData(d);
    onHead({ total: d.stats.total, daysLeft: d.stats.days_left });
  }).catch((e) => setError(e.message)), [onHead]);
  useEffect(() => { load(); }, [load]);

  const focus = data?.focus ?? null;
  // focus decides what the scheduler may pick next, so the whole payload is stale after it changes
  const setFocus = (tag: string | null) => { post("/focus", { tag }).then(load).catch(() => {}); };

  const by = useMemo(() => new Map((data?.tasks ?? []).map((e) => [e.slug, e])), [data]);
  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return (data?.tasks ?? []).filter((e) =>
      (!needle || e.title.toLowerCase().includes(needle) || e.slug.includes(needle) || String(e.topic).padStart(3, "0").includes(needle)) &&
      (!status || e.status === status) &&
      (!focus || e.tier === focus || e.track === focus) &&
      activeTags.every((t) => e.tags.includes(t)));
  }, [data, q, status, focus, activeTags]);

  if (error) return <EmptyState message={`Could not load the catalogue: ${error}`} />;
  if (!data) return <EmptyState message="Loading…" />;

  const { today, stats } = data;
  const pick = (slugs: string[]) => slugs.map((s) => by.get(s)).filter(Boolean) as Row[];
  const review = pick(today.review), fresh = pick(today.new);
  const filtered = !!(q || status || activeTags.length || focus);
  const clear = () => { setQ(""); setStatus(""); setActiveTags([]); if (focus) setFocus(null); };
  const toggleTag = (t: string) => setActiveTags((a) => a.includes(t) ? a.filter((x) => x !== t) : [...a, t]);
  const toggleTier = (t: string) => setOpenTiers((o) => {
    const next = { ...o, [t]: !(o[t] ?? t === focus) };
    localStorage.setItem(OPEN_KEY, JSON.stringify(next));
    return next;
  });
  const todayLine = [
    review.length ? plural(review.length, "review") : "nothing due",
    fresh.length ? `${fresh.length} new ${fresh.length === 1 ? "pick" : "picks"}` : null,
    `${today.done_today} done today`,
  ].filter(Boolean).join(" · ");

  return (
    <div style={{ maxWidth: 1180, margin: "0 auto", display: "grid", gap: 18 }}>
      <Stats boxes={stats.boxes} due={stats.due} seen={stats.seen} total={stats.total} daysLeft={stats.days_left} ladderHref="#/progress" />

      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <span style={LABEL}>Today</span>
        <span className="tabular" style={FAINT}>{todayLine}</span>
      </div>

      {review.length + fresh.length === 0 ? (
        <div className="m-drop"><Card padding={4}>
          <EmptyState message="Nothing due. Pick anything below, or rest — that's training too." />
        </Card></div>
      ) : (
        <Card padding="6px 18px">
          <div className="m-stagger">
            {review.map((e) => <TodayRow key={e.slug} row={e} />)}
            <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 0 6px", borderTop: "1px solid var(--border)" }}>
              <span style={LABEL}>New picks</span>
              <span style={FAINT}>{focus ? `from ${focus}` : "any"}</span>
            </div>
            {fresh.length
              ? fresh.map((e) => <TodayRow key={e.slug} row={e} />)
              : <EmptyState align="left" message="No new picks left today — the ones you started are above." style={{ padding: "4px 0 10px" }} />}
          </div>
        </Card>
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 6, flexWrap: "wrap" }}>
        <Input value={q} onChange={setQ} placeholder="search title or topic…" style={{ width: 260 }} />
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
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", maxHeight: 92, overflowY: "auto" }}>
        {data.tags.map((t) => <TagChip key={t} label={t} active={activeTags.includes(t)} onClick={() => toggleTag(t)} />)}
      </div>

      {rows.length === 0
        ? <div className="m-drop"><Card padding={0}><EmptyState message="No task matches those filters. Loosen a tag or clear the search." actionLabel="Clear filters" onAction={clear} /></Card></div>
        : data.tiers.map((tier) => {
            const group = rows.filter((e) => e.tier === tier);
            return group.length ? <TierGroup key={tier} tier={tier} rows={group} open={openTiers[tier] ?? tier === focus} onToggle={() => toggleTier(tier)} /> : null;
          })}
    </div>
  );
}
