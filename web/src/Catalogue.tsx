import { useEffect, useMemo, useState } from "react";
import { Card, EmptyState, Input, LadderMeter, StatusBadge, TagChip } from "./ds/index.js";
import { api, type Catalogue as Payload, type Row } from "./api";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)" };
const STATUSES = ["all", "new", "due", "open", "done", "scheduled"] as const;

function Line({ ex, today }: { ex: Row; today?: boolean }) {
  const [hover, setHover] = useState(false);
  return (
    <a href={`#/ex/${encodeURIComponent(ex.slug)}`}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{ display: "flex", alignItems: "center", gap: 14, padding: "0 16px", height: today ? 46 : 44, color: "var(--text)", background: hover ? "var(--surface-2)" : "transparent", borderTop: today ? "none" : "1px solid var(--border)", textDecoration: "none" }}>
      <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-faint)", width: 30, textAlign: "right" }}>{ex.topic}</span>
      <span style={{ fontSize: today ? 14.5 : 15, fontWeight: today ? 500 : 400, flex: 1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{ex.title}</span>
      {ex.tags.slice(0, 3).map((t) => <TagChip key={t} label={t} small />)}
      <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 12.5, color: "var(--text-muted)", width: 40, textAlign: "right" }}>{ex.minutes} m</span>
      {/* the API numbers boxes 0-4; the meter fills 1-5, and an unseen card sits on no rung */}
      <LadderMeter box={ex.seen ? ex.box + 1 : 0} />
      <span style={{ width: 92, display: "flex", justifyContent: "flex-end" }}><StatusBadge status={ex.status} /></span>
    </a>
  );
}

export function Catalogue({ onHead, focus }: { onHead: (h: { focus: string | null; tags: string[]; total: number; daysLeft: number }) => void; focus: string | null }) {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [activeTags, setActiveTags] = useState<string[]>([]);
  const [status, setStatus] = useState<string>("all");

  useEffect(() => {
    api<Payload>("/catalogue").then((d) => {
      setData(d);
      onHead({ focus: d.focus, tags: d.tags, total: d.stats.total, daysLeft: d.stats.days_left });
    }).catch((e) => setError(e.message));
  }, [onHead]);

  const by = useMemo(() => new Map((data?.exercises ?? []).map((e) => [e.slug, e])), [data]);
  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return (data?.exercises ?? []).filter((e) =>
      (!needle || e.title.toLowerCase().includes(needle) || e.slug.includes(needle) || String(e.topic) === needle) &&
      activeTags.every((t) => e.tags.includes(t)) &&
      (status === "all" || e.status === status));
  }, [data, q, activeTags, status]);

  if (error) return <EmptyState message={`Could not load the catalogue: ${error}`} />;
  if (!data) return <EmptyState message="Loading…" />;

  const { today, stats } = data;
  const pick = (slugs: string[]) => slugs.map((s) => by.get(s)).filter(Boolean) as Row[];
  const review = pick(today.review), fresh = pick(today.new);
  const toggleTag = (t: string) => setActiveTags((a) => a.includes(t) ? a.filter((x) => x !== t) : [...a, t]);

  return (
    <div style={{ maxWidth: 1080, margin: "0 auto", display: "grid", gap: 20 }}>
      <div style={{ display: "flex", gap: 20, alignItems: "baseline", flexWrap: "wrap" }}>
        <span style={LABEL}>Today</span>
        <span className="tabular" style={{ fontSize: 13, color: "var(--text-faint)" }}>
          due {stats.due} · started {stats.seen} / {stats.total} · {today.done_today} done today
          {focus ? ` · new picks limited to “${focus}”` : ""}
        </span>
      </div>
      <Card padding={"6px 0"}>
        {review.length + fresh.length === 0
          ? <EmptyState message="Nothing due. Pick anything below, or rest — that's training too." />
          : <>
              {review.map((e) => <Line key={e.slug} ex={e} today />)}
              {review.length && fresh.length ? <div style={{ borderTop: "1px solid var(--border)", margin: "4px 0" }} /> : null}
              {fresh.map((e) => <Line key={e.slug} ex={e} today />)}
            </>}
      </Card>

      <div style={{ display: "flex", gap: 20, alignItems: "baseline", marginTop: 6 }}>
        <span style={LABEL}>All drills</span>
        <span className="tabular" style={{ fontSize: 13, color: "var(--text-faint)" }}>{rows.length} shown</span>
      </div>
      <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <Input placeholder="search title, slug or topic…" value={q} onChange={setQ} style={{ width: 300 }} />
        <span style={{ fontSize: 13, color: "var(--text-faint)" }}>status:</span>
        {STATUSES.map((s) => <TagChip key={s} label={s} active={status === s} onClick={() => setStatus(s)} />)}
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {data.tags.map((t) => <TagChip key={t} label={t} active={activeTags.includes(t)} onClick={() => toggleTag(t)} />)}
      </div>
      <Card padding={0} style={{ overflow: "hidden" }}>
        {rows.length === 0
          ? <EmptyState message="Nothing matches. Clear a filter or two." actionLabel="Clear filters" onAction={() => { setQ(""); setActiveTags([]); setStatus("all"); }} />
          : rows.map((e) => <Line key={e.slug} ex={e} />)}
      </Card>
    </div>
  );
}
