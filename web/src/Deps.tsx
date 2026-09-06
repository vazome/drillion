import { useEffect, useState } from "react";
import { Button, Card, DepLineage, EmptyState } from "./ds/index.js";
import { api, type Task as TaskData } from "./api";

export const taskHref = (slug: string) => `#/task/${encodeURIComponent(slug)}`;
/** Every prereq link goes to that task's own lineage, not to the task: you follow these to
 *  walk the graph, and `Open NNN →` is how you leave it for the editor. */
export const depsHref = (slug: string) => `${taskHref(slug)}/deps`;

/** Payloads already fetched, so walking the graph swaps a board rather than reloading a
 *  screen. Task payloads are read-only here and cheap; a session-lived map is the whole
 *  cache, and a `progress.json` write anywhere else in the app never reaches this screen. */
const seen = new Map<string, TaskData>();
const inflight = new Map<string, Promise<TaskData>>();

/** Fetch a lineage before it is asked for — a node calls this on hover and on focus, which
 *  is most of the way through the click. */
export function prefetch(slug: string): Promise<TaskData> {
  const hit = seen.get(slug) ?? inflight.get(slug);
  if (hit) return Promise.resolve(hit);
  const p = api<TaskData>(`/task/${encodeURIComponent(slug)}`)
    .then((task) => { seen.set(slug, task); return task; })
    .finally(() => inflight.delete(slug));
  inflight.set(slug, p);
  return p;
}

/** The lineage as a screen of its own, reached from a catalogue row's `needs` flag: you are
 *  scanning the list, not mid-attempt, so there is nothing behind this to preserve. The
 *  panel over the task screen is the other end — see `Task.tsx`. */
export function Deps({ slug }: { slug: string }) {
  // straight out of the cache when a hover already paid for it: no loading state, no flash
  const [task, setTask] = useState<TaskData | null>(() => seen.get(slug) ?? null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    prefetch(slug)
      .then((p) => live && setTask(p))
      .catch((e) => live && setError(e.message));
    return () => { live = false; };
  }, [slug]);

  if (error) return <EmptyState message={`Could not load ${slug}: ${error}`} actionLabel="Back to Today" onAction={() => { location.hash = "#/"; }} />;
  if (!task) return <EmptyState message="Loading…" />;

  const { topic, title } = task.meta;
  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", display: "grid", gap: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
        <a href="#/" style={{ fontSize: 13, whiteSpace: "nowrap" }}>← Catalogue</a>
        <div style={{ flex: 1 }} />
        <Button variant="secondary" onClick={() => { location.hash = taskHref(task.slug); }}>
          Open {String(topic).padStart(3, "0")} →
        </Button>
      </div>
      <Card label={`Lineage · ${task.slug}`}>
        <DepLineage
          task={{ topic, title, tags: task.meta.tags, box: task.box, aside: `${task.status} · ${task.seen ? `seen ${task.seen}×` : "never seen"}` }}
          requires={task.requires} unlocks={task.unlocks} ladder={task.ladder}
          hrefOf={(r) => depsHref(r.slug)} onPrefetch={(r) => { void prefetch(r.slug); }} />
      </Card>
    </div>
  );
}
