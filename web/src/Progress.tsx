import { useEffect, useState } from "react";
import { Card, EmptyState, Ladder, StatusBadge, Table } from "./ds/index.js";
import { api, type Progress as Payload } from "./api";
import { Stats } from "./Stats";

const mmss = (s: number) => `${Math.floor(s / 60)}m${String(s % 60).padStart(2, "0")}s`;
/** "2026-08-26" → "26 Aug". Parsed at local midnight so the day never slips a timezone. */
const day = (iso: string) => new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { day: "numeric", month: "short" });

export type TagKey = "tag" | "seen" | "total" | "share";
export type TagRow = { id: string; tag: string; seen: number; total: number; share: number };

/** `share` is kept a number and rendered with the %, so 10% sorts above 9%. */
const TAG_COLS = [
  { key: "tag", label: "Tag", sortable: true },
  { key: "seen", label: "Seen", align: "right" as const, mono: true, width: "62px", sortable: true },
  { key: "total", label: "Total", align: "right" as const, mono: true, width: "62px", sortable: true, muted: true },
  { key: "share", label: "Share", align: "right" as const, mono: true, width: "66px", sortable: true, render: (r: TagRow) => `${r.share}%` },
];

const LOG_COLS = [
  { key: "date", label: "Date", width: "76px", mono: true, muted: true, render: (r: LogRow) => day(r.date) },
  { key: "slug", label: "Task", mono: true, render: (r: LogRow) => <a href={`#/task/${encodeURIComponent(r.slug)}`}>{r.slug}</a> },
  { key: "grade", label: "Grade", width: "96px", render: (r: LogRow) => <StatusBadge status={r.grade} /> },
  { key: "attempts", label: "Attempts", align: "right" as const, mono: true, width: "84px", muted: true },
  { key: "time", label: "Active", align: "right" as const, mono: true, width: "76px" },
  { key: "kind", label: "Kind", width: "62px", small: true, muted: true },
];
type LogRow = Payload["log"][number];

/** Sort the coverage rows: numbers compare numerically (10% above 9%), and ties keep the
 *  API's order because Array.sort is stable. Exported so a check can drive it directly. */
export function sortTags(rows: TagRow[], key: TagKey, dir: "asc" | "desc"): TagRow[] {
  const d = dir === "asc" ? 1 : -1;
  return [...rows].sort((a, b) => (key === "tag" ? a.tag.localeCompare(b.tag) : a[key] - b[key]) * d);
}

export function Progress() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sort, setSort] = useState<{ key: TagKey; dir: "asc" | "desc" }>({ key: "seen", dir: "desc" });
  useEffect(() => { api<Payload>("/progress").then(setData).catch((e) => setError(e.message)); }, []);

  if (error) return <EmptyState message={`Could not load progress: ${error}`} />;
  if (!data) return <EmptyState message="Loading…" />;

  const tagRows = sortTags(Object.entries(data.per_tag).map(([tag, t]) => (
    { id: tag, tag, seen: t.seen, total: t.total, share: t.total ? Math.round((t.seen / t.total) * 100) : 0 }
  )), sort.key, sort.dir);

  const logRows = [...data.log].reverse().map((row, i) => ({ ...row, id: i, time: mmss(row.secs), kind: row.new ? "new" : "review" }));

  return (
    <div style={{ maxWidth: 1180, margin: "0 auto", display: "grid", gap: 18 }}>
      <Stats boxes={data.boxes} due={data.due} seen={data.seen} total={data.total} />

      <Card label="The ladder">
        <Ladder boxes={data.boxes} />
        <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 12 }}>
          <span style={{ fontSize: 13, color: "var(--text-muted)" }}>A quick pass climbs two boxes, a pass one, struggled none — and box 5 is the ceiling. Each box returns on its own interval.</span>
          <div style={{ flex: 1 }} />
          <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 12.5, color: "var(--text-faint)" }}>
            {data.seen} cards on the ladder · {data.total - data.seen} untouched
          </span>
        </div>
      </Card>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(360px, 420px) minmax(0, 1fr)", gap: 18, alignItems: "start" }}>
        <Card label="Coverage by tag" padding={16}>
          {/* 70-odd tags: scroll the body, same as the log, so the two cards stay level. */}
          <div style={{ maxHeight: 520, overflow: "auto" }}>
            <Table columns={TAG_COLS} rows={tagRows} sortKey={sort.key} sortDir={sort.dir}
              onSort={(key, d) => setSort({ key: key as TagKey, dir: d })}
              emptyMessage="No tags yet." />
          </div>
        </Card>

        <Card label="Last 30 sessions" padding={16}>
          <div style={{ maxHeight: 520, overflow: "auto" }}>
            <Table columns={LOG_COLS} rows={logRows} emptyMessage="No passes logged yet. The first one lands here." />
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 10, fontSize: 12.5, color: "var(--text-faint)" }}>
            <span>QUICK · first try, under par</span><span>·</span><span>PASS</span><span>·</span><span>STRUGGLED</span><span>·</span><span>abandoned</span>
          </div>
        </Card>
      </div>
    </div>
  );
}
