import { useEffect, useState } from "react";
import { Card, DueForecast, EmptyState, Ladder, PracticeHeatmap, StatusBadge, Table, TopicStrips } from "./ds/index.js";
import { api, type Progress as Payload } from "./api";
import { Stats } from "./Stats";

const mmss = (s: number) => `${Math.floor(s / 60)}m${String(s % 60).padStart(2, "0")}s`;
/** "2026-08-26" → "26 Aug". Parsed at local midnight so the day never slips a timezone. */
const day = (iso: string) => new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { day: "numeric", month: "short" });

const LOG_COLS = [
  { key: "date", label: "Date", width: "76px", mono: true, muted: true, render: (r: LogRow) => day(r.date) },
  { key: "slug", label: "Task", mono: true, render: (r: LogRow) => <a href={`#/task/${encodeURIComponent(r.slug)}`}>{r.slug}</a> },
  { key: "grade", label: "Grade", width: "96px", render: (r: LogRow) => <StatusBadge status={r.grade} /> },
  { key: "attempts", label: "Attempts", align: "right" as const, mono: true, width: "84px", muted: true },
  { key: "time", label: "Active", align: "right" as const, mono: true, width: "76px" },
  { key: "kind", label: "Kind", width: "62px", small: true, muted: true },
];
type LogRow = Payload["log"][number];

export function Progress() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api<Payload>("/progress").then(setData).catch((e) => setError(e.message)); }, []);

  if (error) return <EmptyState message={`Could not load progress: ${error}`} />;
  if (!data) return <EmptyState message="Loading…" />;

  const tags = Object.entries(data.per_tag).map(([tag, t]) => ({ tag, ...t }));
  const logRows = [...data.log].reverse().map((row, i) => ({ ...row, id: i, time: mmss(row.secs), kind: row.new ? "new" : "review" }));

  return (
    <div style={{ maxWidth: 1180, margin: "0 auto", display: "grid", gap: 18 }}>
      <Stats boxes={data.boxes} ladder={data.ladder} due={data.due} seen={data.seen} total={data.total} practised={data.practised} outOf={data.window} />

      <Card label="The ladder">
        <Ladder boxes={data.boxes} intervals={data.ladder} />
        <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 12 }}>
          <span style={{ fontSize: 13, color: "var(--text-muted)" }}>A quick pass climbs two boxes, a pass one, and a struggle costs one — box {data.ladder.length} is the ceiling. Each box returns on its own interval.</span>
          <div style={{ flex: 1 }} />
          <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 12.5, color: "var(--text-faint)" }}>
            {data.seen} cards on the ladder · {data.total - data.seen} untouched
          </span>
        </div>
      </Card>

      <Card label="Due load · next 14 days"><DueForecast forecast={data.forecast} cap={data.cap} today={data.today} /></Card>
      <Card label="Practice"><PracticeHeatmap days={data.days} today={data.today} /></Card>
      <Card label="Topic depth" padding={16}><TopicStrips tags={tags} /></Card>

      <Card label="Last 30 sessions" padding={16}>
        <div style={{ maxHeight: 420, overflow: "auto", paddingRight: 10 }}>
          <Table columns={LOG_COLS} rows={logRows} emptyMessage="No passes logged yet. The first one lands here." />
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 10, fontSize: 12.5, color: "var(--text-faint)" }}>
          <span>QUICK · first try, under par</span><span>·</span><span>PASS</span><span>·</span><span>STRUGGLED</span><span>·</span><span>abandoned</span>
        </div>
      </Card>
    </div>
  );
}
