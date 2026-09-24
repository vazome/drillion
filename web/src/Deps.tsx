import { useEffect, useState } from "react";
import { Icon, DepLineage, EmptyState, TaskPath } from "./ds/index.js";
import { api, type Task as TaskData } from "./api";
import { strength } from "./strength";
import { topicNo } from "./format";
import { Level } from "./Level";
import { useNarrow } from "./narrow";
import s from "./Deps.module.css";

export const taskHref = (slug: string) => `#/task/${encodeURIComponent(slug)}`;
/** Every prereq link goes to that task's own lineage, not to the task: you follow these to
 *  walk the graph, and `Open NNN` is how you leave it for the editor. */
export const depsHref = (slug: string) => `${taskHref(slug)}/deps`;

/** Payloads fetched a moment ago, so walking the graph swaps a board rather than reloading a
 *  screen. A hit only lives as long as a hover takes to become a click: a pass, an abandon or
 *  a reset elsewhere changes these payloads, and a longer-lived copy would show the old one. */
const FRESH_MS = 10_000;
const seen = new Map<string, { task: TaskData; at: number }>();
const inflight = new Map<string, Promise<TaskData>>();
const fresh = (slug: string) => {
  const hit = seen.get(slug);
  return hit && Date.now() - hit.at < FRESH_MS ? hit.task : undefined;
};

/** Fetch a lineage before it is asked for — a node calls this on hover and on focus, which
 *  is most of the way through the click. */
export function prefetch(slug: string): Promise<TaskData> {
  const hit = fresh(slug) ?? inflight.get(slug);
  if (hit) return Promise.resolve(hit);
  const p = api<TaskData>(`/task/${encodeURIComponent(slug)}`)
    .then((task) => { seen.set(slug, { task, at: Date.now() }); return task; })
    .finally(() => inflight.delete(slug));
  inflight.set(slug, p);
  return p;
}

/** The lineage as a screen of its own, reached from a catalogue row's `needs` flag: you are
 *  scanning the list, not mid-attempt, so there is nothing behind this to preserve. The
 *  panel over the task screen is the other end — see `Task.tsx`. */
export function Deps({ slug }: { slug: string }) {
  // straight out of the cache when a hover already paid for it: no loading state, no flash
  const [task, setTask] = useState<TaskData | null>(() => fresh(slug) ?? null);
  const [error, setError] = useState<string | null>(null);
  const narrow = useNarrow();

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
    <div className={s.page}>
      <header className={s.head}>
        <div className={s.headText}>
          <a href="#/" className={s.back}><Icon name="ArrowLeft" size={14} />Back to the catalogue</a>
          <h1 className={s.h1}><span className={s.num}>{topicNo(topic)}</span>{title}</h1>
          <p className={s.muted}>What it needs, and what it opens. Any task can be opened, whatever it builds on.</p>
        </div>
        <a href={taskHref(task.slug)} className={s.open}>Open {topicNo(topic)}<Icon name="ArrowRight" size={14} /></a>
      </header>
      <section aria-label={`Connections of ${topicNo(topic)}`} className={s.card}>
        <DepLineage task={{ topic, title, tags: task.meta.tags, aside: <Centre task={task} /> }}
          requires={task.requires} unlocks={task.unlocks} stacked={narrow}
          hrefOf={(r) => depsHref(r.slug)} onPrefetch={(r) => { void prefetch(r.slug); }} />
      </section>
    </div>
  );
}

/** The foot of the centre card: where the task sits, how hard it is, and where it stands. */
export function Centre({ task }: { task: TaskData }) {
  const known = strength(task.box, !!task.seen, task.ladder);
  return <>
    <TaskPath tier={task.meta.tier} track={task.meta.track} tags={task.meta.tags} />
    <span>{task.meta.difficulty}</span><span>{task.status}</span>
    {known ? <Level of={known} /> : null}
  </>;
}
