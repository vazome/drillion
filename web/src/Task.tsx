import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Button, Card, Collapsible, ConflictBanner, DepLineage, EmptyState, LadderMeter, NoteField, NoticeBanner, RequiresTag, ResultBanner, RowFlags, SpecText, StatusBadge, TagChip, TaskPath, Timer, StuckNudge } from "./ds/index.js";
import { ApiError, api, post, type Task as TaskData, type RunResult } from "./api";
import { depsHref, prefetch } from "./Deps";
import { DiffView, Editor } from "./Editor";
import { useDraft } from "./useDraft";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)" };
const ASIDE = { fontSize: 12.5, color: "var(--text-faint)" };
const PLAIN = { fontWeight: 400, textTransform: "none" as const, letterSpacing: 0, ...ASIDE };
const ATTEMPT_MS = 5000;    // reading the task is work: the clock starts once the page settles
const HEARTBEAT_MS = 60_000;
// long enough for `role="status"` to finish speaking the message before the node goes
const GATE_MS = 4000;
/** Below this the two panes stack, spec first. A tablet is for reading a spec and running it,
 *  never for writing code side by side. Both arguments are module constants: rebuilt every
 *  render, they would make `useSyncExternalStore` re-subscribe every render. */
const NARROW = "(max-width: 999px)";
const watchNarrow = (onChange: () => void) => {
  const q = matchMedia(NARROW);
  q.addEventListener("change", onChange);
  return () => q.removeEventListener("change", onChange);
};
const isNarrow = () => matchMedia(NARROW).matches;
const secs = (n: number) => n >= 60 ? `${Math.floor(n / 60)}m${String(n % 60).padStart(2, "0")}s` : `${n}s`;
const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

/** A refused action, shown beside the control that asked for it. */
type Gate = { at: "hints" | "solution" | "editor" | "note"; message: string } | null;

/** `ran` is an ungraded Run that came back green: the tests pass, nothing moved. Only
 *  `passed` is a graded pass, and only it ends the attempt. */
type Result =
  | { state: "idle" | "running" }
  | { state: "ran"; output: string }
  | { state: "failed"; graded: boolean; attempts: number; headline: string; output: string }
  | { state: "passed"; grade: string; box: number; stepped: boolean; fromBox: number; reason: string; dueIn: number; attempts: number; code: string };

/** The pass banner's one line about the card: `stepped` is the server's answer to whether
 *  the card moved, and `box` against `fromBox` says which way. */
export function stepLine(grade: string, box: number, fromBox: number, stepped: boolean, boxes: number) {
  if (stepped) return box < fromBox ? "the card stepped back a box — it comes back sooner" : "the card stepped up";
  if (box === boxes - 1) return "the card is already in the top box and stays there";
  if (box === 0) return "the card is already in the first box and stays there";
  return `${grade} keeps the card where it is`;
}

/** The header chips: `requires ✓019 ▲040`. Titles are dropped past two — the row is
 *  already crowded, and a number-only tag still links. */
function RequiresChips({ requires }: { requires: TaskData["requires"] }) {
  if (!requires.length) return null;
  const withTitles = requires.length <= 2 && requires.every((r) => r.title.length < 30);
  return (
    <>
      <span style={{ ...LABEL, fontSize: 11, color: "var(--text-faint)", marginLeft: 4 }}>requires</span>
      {requires.map((r) => (
        <RequiresTag key={r.slug} topic={r.topic} title={withTitles ? r.title : undefined}
          state={r.state} href={depsHref(r.slug)} onPointerEnter={() => { void prefetch(r.slug); }} />
      ))}
    </>
  );
}

export function Task({ slug, dark }: { slug: string; dark: boolean }) {
  const [task, setTask] = useState<TaskData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Result>({ state: "idle" });
  const [gate, setGate] = useState<Gate>(null);
  const [active, setActive] = useState(0);
  const [nextHintIn, setNextHintIn] = useState<number | null>(null);
  const [nextSlug, setNextSlug] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);          // a hint spent twice cannot be un-spent
  const [nudge, setNudge] = useState(false);        // the server's offer of a hint, not ours
  const [nudgeOff, setNudgeOff] = useState(false);
  const [inflight, setInflight] = useState<"run" | "submit" | null>(null);
  const [lineage, setLineage] = useState(false);
  const narrow = useSyncExternalStore(watchNarrow, isNarrow);

  const gateTimer = useRef<number | undefined>(undefined);
  const unlocksBtn = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);
  const dropped = useRef(false);             // discarded here: do not re-open the attempt behind them
  const hasAttempt = !!task?.attempt;
  const passed = result.state === "passed";
  const url = `/task/${encodeURIComponent(slug)}`;

  /** Everything a task payload says that is not the draft's business. */
  const onPayload = useCallback((p: TaskData) => {
    setTask(p);
    setActive(p.attempt?.active ?? 0);
    setNextHintIn(p.hints.next_in);
    setNudge(p.nudge);
  }, []);

  const onSaveError = useCallback((message: string, at: "editor" | "note" = "editor") => setGate({ at, message }), []);
  const { code, dirty, syntaxBad, conflict, offer, note, noteDirty, adopt, reset, edit, editNote,
    landed, ensureOpen, current, pending, settle, takeDisk, keepMine, discard, restore, absorb } =
    useDraft(slug, onPayload, onSaveError);

  /** A notice that says one thing and gets out of the way — the hint gate's whole UI. */
  const flash = useCallback((message: string) => {
    const mine: Gate = { at: "hints", message };
    setGate(mine);
    clearTimeout(gateTimer.current);
    // nine other callers write this slot: the timer takes back only its own notice
    gateTimer.current = setTimeout(() => setGate((g) => (g === mine ? null : g)), GATE_MS);
  }, []);

  useEffect(() => {
    let live = true;
    api<TaskData>(url).then((p) => live && reset(p)).catch((e) => live && setError(e.message));
    return () => { live = false; };
  }, [url, reset]);

  // the page opens its own attempt once it has sat open; the delay skips a mis-click
  useEffect(() => {
    if (!task || hasAttempt || passed || dropped.current) return;
    const t = setTimeout(() => { ensureOpen().catch(() => {}); }, ATTEMPT_MS);
    return () => clearTimeout(t);
  }, [task, hasAttempt, passed, ensureOpen]);

  useEffect(() => () => clearTimeout(gateTimer.current), []);

  useEffect(() => {
    if (!dirty && !noteDirty) return;
    const warn = (e: BeforeUnloadEvent) => e.preventDefault();
    addEventListener("beforeunload", warn);
    return () => removeEventListener("beforeunload", warn);
  }, [dirty, noteDirty]);

  // local ticks between heartbeats, server truth on every touch
  useEffect(() => {
    if (!hasAttempt || passed) return;
    const tick = setInterval(() => {
      if (document.visibilityState === "visible") {
        setActive((s) => s + 1);
        setNextHintIn((n) => (n === null ? null : Math.max(0, n - 1)));
      }
    }, 1000);
    const beat = setInterval(() => {
      if (document.visibilityState !== "visible") return;
      post<{ active: number; nudge: boolean }>(`/task/${encodeURIComponent(slug)}/touch`)
        .then((r) => { setActive(r.active); setNudge(r.nudge); }).catch(() => {});
    }, HEARTBEAT_MS);
    return () => { clearInterval(tick); clearInterval(beat); };
  }, [hasAttempt, passed, slug]);

  /** Run and Submit are the same round trip; `submit` is the learner saying they are done.
   *  Only a submitted run costs an attempt and moves the card — a Run is free, repeatable,
   *  and grades nothing however green it comes back. */
  const go = async (submit: boolean) => {
    setInflight(submit ? "submit" : "run");
    setResult({ state: "running" });
    try {
      await settle();                // ride the etag the pending PUT returns
      await ensureOpen();
      const r = await post<RunResult>(`${url}/run`, { ...current(), submit });
      landed(r.etag, r.passed && r.graded ? r.code : undefined);
      setNudge(false);                     // a run answers the nudge, whichever way it went
      if (r.passed && r.graded) {
        setResult({ state: "passed", grade: r.grade, box: r.box, stepped: r.stepped, fromBox: r.from_box, reason: r.reason, dueIn: r.due_in, attempts: r.attempts, code: r.code });
        setTask((p) => p && ({ ...p, reference: r.reference, lapses: r.lapses }));
        setNextSlug(r.next);
      } else if (r.passed) {
        setResult({ state: "ran", output: r.output });
      } else {
        setResult({ state: "failed", graded: r.graded, attempts: r.attempts, headline: r.headline.join("\n") || "The tests did not pass.", output: r.output });
        setTask((p) => p && p.attempt ? { ...p, attempt: { ...p.attempt, attempts: r.attempts } } : p);
      }
    } catch (e) {
      const err = e as ApiError, bad = err.status === 400;
      if (absorb(err) && !bad) setResult({ state: "idle" });      // the conflict banner has it now
      else setResult({ state: "failed", graded: submit, attempts: 0, output: "",
        headline: bad ? `${err.detail?.error}${err.detail?.line != null ? ` (line ${err.detail.line})` : ""}` : err.message });
    } finally { setInflight(null); }
  };
  const run = () => { void go(false); };
  const submit = () => { void go(true); };

  /** The lineage panel, not a navigation: it opens mid-attempt, so the editor buffer, the
   *  run state and the timer all have to survive it. */
  const closeLineage = useCallback(() => { setLineage(false); unlocksBtn.current?.focus(); }, []);
  useEffect(() => {
    if (!lineage) return;
    panel.current?.focus();
    const on = (e: globalThis.KeyboardEvent) => { if (e.key === "Escape") closeLineage(); };
    addEventListener("keydown", on);
    return () => removeEventListener("keydown", on);
  }, [lineage, closeLineage]);

  const hint = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await pending();               // the payload carries an etag: never over a live PUT
      await ensureOpen();
      adopt(await post<TaskData>(`${url}/hint`));
      setGate(null);
    } catch (e) {
      const err = e as ApiError;
      const wait = err.status === 423 ? err.detail?.wait_secs : 0;
      if (wait) {
        setNextHintIn(wait);
        flash(`Not yet — ${secs(wait)}. Keep working; hint ${(task?.hints.shown.length ?? 0) + 1} unlocks itself.`);
      } else setGate({ at: "hints", message: err.message });
    } finally { setBusy(false); }
  };

  const solution = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await pending();               // the payload carries an etag: never over a live PUT
      await ensureOpen();
      adopt(await post<TaskData>(`${url}/solution`));
      setGate(null);
    } catch (e) {
      const err = e as ApiError;
      const d = err.detail ?? {};
      setGate({ at: "solution", message: d.need_attempts || d.need_secs
        ? `${err.message} — ${plural(d.need_attempts || 0, "more attempt")}, ${secs(d.need_secs || 0)} more work.`
        : err.message });
    } finally { setBusy(false); }
  };

  const abandon = async () => {
    if (!confirm("Discard this attempt? The work is archived and the stub comes back.")) return;
    await settle();
    try {
      const p = await post<TaskData>(`${url}/abandon`, { etag: current().etag });
      discard();
      dropped.current = true;
      reset(p); setResult({ state: "idle" }); setGate(null); setNextSlug(null);
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 400 || !absorb(err)) setGate({ at: "editor", message: err.message });
    }
  };

  /** Not today: the card keeps its box, due date and counts, and tomorrow puts it back.
   * The catalogue's Buried band is the other end of this control. */
  const bury = async () => {
    if (!task) return;
    try {
      const r = await post<{ buried: boolean }>(`/task/${encodeURIComponent(slug)}/bury`, { buried: !task.buried });
      setTask({ ...task, buried: r.buried });
    } catch (e) {
      setGate({ at: "editor", message: (e as ApiError).message });
    }
  };

  /** The nudge's second offer: put the task aside for today and go read up. */
  const buryAndLeave = async () => {
    try {
      await post(`/task/${encodeURIComponent(slug)}/bury`, { buried: true });
      location.hash = "#/";
    } catch (e) {
      setGate({ at: "editor", message: (e as ApiError).message });
    }
  };

  if (error) return <EmptyState message={`Could not load ${slug}: ${error}`} actionLabel="Back to Today" onAction={() => { location.hash = "#/"; }} />;
  if (!task) return <EmptyState message="Loading…" />;

  const { meta, hints, solution: gateState, attempt, reference } = task;
  const hintsLeft = hints.total - hints.shown.length;
  const hintReady = nextHintIn === null || nextHintIn <= 0;
  /** Peeked this sitting or earned by passing; `solution_shown` survives a reload, and still costs. */
  const peeked = !!attempt?.solution_shown;
  const flagged = task.lapses >= task.lapse_limit;
  /** The code to diff against the reference: this sitting's pass, else the last archived one.
   *  A peek has no passing code of its own, and an abandoned draft is archived with code too. */
  const mine = passed ? result.code
    : peeked ? ""
    : task.archive.filter((a) => a.code && a.grade !== "abandoned").at(-1)?.code ?? "";
  /** The gate banner, under the control that raised it. The container stays in the tree so
   * screen readers have a live region to announce into. */
  const notice = (at: Exclude<Gate, null>["at"]) => (
    <div role="status" style={{ marginTop: gate?.at === at ? 10 : 0 }}>
      {gate?.at === at ? <div className="m-drop"><NoticeBanner message={gate.message} actions={[{ label: "Dismiss", onClick: () => setGate(null) }]} /></div> : null}
    </div>
  );

  const runNo = passed ? result.attempts : attempt ? attempt.attempts + 1 : 0;   // the attempt you are on
  // an ungraded Run cost no attempt, so the card must not number it as one
  const ungraded = result.state === "ran" || (result.state === "failed" && !result.graded);
  const resultNo = !ungraded && "attempts" in result ? result.attempts : 0;   // the attempt this result came from
  const fell = passed && result.stepped && result.box < result.fromBox;

  return (
    <div style={{ maxWidth: 1500, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 14 }}>
        <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-faint)" }}>{String(meta.topic).padStart(3, "0")}</span>
        <h1 style={{ margin: 0, fontSize: "var(--fs-h)", fontWeight: 600 }}>{meta.title}</h1>
        <StatusBadge status={task.status} />
        <StatusBadge status={meta.difficulty} />
        <RequiresChips requires={task.requires} />
        <RowFlags buried={task.buried} lapses={task.lapses} lapseLimit={task.lapse_limit} />
        <div style={{ flex: 1 }} />
        {meta.track ? <TagChip label={meta.track} small /> : null}
        {task.unlocks.length ? (
          <button type="button" ref={unlocksBtn} onClick={() => setLineage(true)} aria-expanded={lineage}
            style={{ background: "transparent", border: "none", padding: 0, font: "inherit", fontSize: 12.5, color: "var(--accent)", cursor: "pointer" }}>
            unlocks {task.unlocks.length} →
          </button>
        ) : null}
        <TaskPath tier={meta.tier} tags={meta.tags} />
        {meta.source ? <span style={ASIDE}>{meta.source}</span> : null}
      </div>

      {lineage ? (
        <div role="dialog" aria-label={`Lineage of ${meta.title}`} onClick={closeLineage} className="m-fade"
          style={{ position: "fixed", inset: 0, zIndex: 40, background: "color-mix(in srgb, var(--text) 28%, transparent)", display: "flex", alignItems: "flex-start", justifyContent: "center", padding: "72px 24px", overflow: "hidden" }}>
          {/* the scroll lives on the animated element, not around it: `m-rise` starts the
            * panel 6px low, and inside a scrolling parent those 6px are overflow — one frame
            * of scrollbar on the way in. An element's own transform never adds to its own
            * scroll content, so putting the two on one box makes the flash impossible. */}
          <div ref={panel} tabIndex={-1} onClick={(e) => e.stopPropagation()} className="m-rise"
            style={{ width: "min(1040px, 100%)", maxHeight: "100%", overflowY: "auto", outline: "none" }}>
            <Card label={`Lineage · ${task.slug}`} style={{ boxShadow: "var(--shadow-pop)" }}>
              <DepLineage task={{ topic: meta.topic, title: meta.title, tags: meta.tags, box: task.box, aside: "attempt still open behind this" }}
                requires={task.requires} unlocks={task.unlocks} ladder={task.ladder}
                hrefOf={(r) => depsHref(r.slug)} onPrefetch={(r) => { void prefetch(r.slug); }} onClose={closeLineage} />
            </Card>
          </div>
        </div>
      ) : null}

      <div style={{ display: "flex", flexDirection: narrow ? "column" : "row", gap: 20, alignItems: narrow ? "stretch" : "flex-start" }}>
        <div style={narrow
          ? { width: "auto" }
          : { width: "42%", minWidth: 340, maxWidth: "70%", maxHeight: "calc(100vh - 148px)", overflow: "auto", resize: "horizontal" }}>
          <Card label={`Spec · ${slug}/README.md`}>
            <SpecText text={task.spec_md} slug={slug} hideTitle />

            <div style={{ marginTop: 22, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
              <div style={{ ...LABEL, marginBottom: 10 }}>
                Hints <span style={PLAIN}>· {hints.shown.length} of {hints.total} shown, unlocked by time on task</span>
              </div>
              {flagged ? (
                <div style={{ ...ASIDE, color: "var(--text-muted)", marginBottom: 10 }}>
                  You have struggled with this {plural(task.lapses, "time")}. The hints below, or the
                  tasks it builds on, are the likelier problem — not you.
                </div>
              ) : null}
              {hints.shown.map((text, i) => (
                <div key={i} style={{ background: "var(--surface-2)", borderRadius: "var(--radius)", padding: "10px 12px", marginBottom: 8 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, letterSpacing: ".04em", textTransform: "uppercase", color: "var(--accent)", marginBottom: 4 }}>Hint {i + 1}</div>
                  <SpecText text={text} slug={slug} style={{ fontSize: 14 }} />
                </div>
              ))}
              {hintsLeft ? (
                <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
                  <Button variant="secondary" onClick={hint} disabled={busy}>Show hint {hints.shown.length + 1}</Button>
                  <span style={ASIDE}>{hintReady ? "ready" : `unlocks in ${secs(nextHintIn!)}`}</span>
                </div>
              ) : (
                <div style={ASIDE}>All {hints.total} levels shown. Nothing else is gated except the solution.</div>
              )}
              {notice("hints")}
            </div>

            <div style={{ marginTop: 20, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
              <div style={{ ...LABEL, marginBottom: 10 }}>
                Solution <span style={PLAIN}>· {peeked ? "revealed — this attempt is marked" : reference ? "open — you passed this one" : gateState.unlocked ? "unlocked" : `locked · needs ${plural(gateState.need_attempts, "more attempt")} and ${secs(gateState.need_secs)} more work`}</span>
              </div>
              {reference ? (
                <div style={{ display: "grid", gap: 8 }}>
                  {peeked
                    ? <NoticeBanner message="Solution shown — this pass won’t promote the card. It grades as struggled and stays in its box." actions={[]} />
                    : <div style={ASIDE}>{mine
                        ? "Your solution on the left, the reference on the right. It closes again when this card comes back."
                        : "The reference answer, for comparison with what you wrote. It closes again when this card comes back."}</div>}
                  {mine
                    ? <DiffView mine={mine} reference={reference} dark={dark} maxHeight="46vh" />
                    : <SpecText text={"```python\n" + reference + "\n```"} slug={slug} />}
                </div>
              ) : (
                <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
                  <Button variant="secondary" onClick={solution} disabled={busy}>{gateState.unlocked ? "Show solution" : "Unlock solution"}</Button>
                  <span style={ASIDE}>taking it means this pass won’t promote</span>
                </div>
              )}
              {notice("solution")}
            </div>

            <div style={{ marginTop: 20, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
              <NoteField value={note} onChange={editNote} dirty={noteDirty}
                ariaLabel={`Your note on ${meta.title}`}
                placeholder="What caught you out? Write it down while you still remember." />
              {notice("note")}
            </div>

            {task.archive.length ? (
              <Collapsible label={`Archive · ${plural(task.archive.length, "previous pass")}`} mono={false} style={{ marginTop: 12 }}>
                {task.archive.slice().reverse().map((a, i) => (
                  <div key={i} style={{ marginBottom: 8 }}>
                    <div style={{ display: "flex", gap: 10, alignItems: "center", fontSize: 13 }}>
                      <span className="tabular" style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>{a.date}</span>
                      <StatusBadge status={a.grade} />
                    </div>
                    {a.code ? <pre style={{ margin: "6px 0 0", fontSize: 12.5, whiteSpace: "pre-wrap", color: "var(--text-muted)" }}>{a.code}</pre> : null}
                  </div>
                ))}
              </Collapsible>
            ) : null}
          </Card>
        </div>

        <div style={{ flex: 1, minWidth: narrow ? 0 : 420, display: "grid", gap: 12 }}>
          {conflict ? <div className="m-drop"><ConflictBanner detail="Your draft and the file on disk have diverged." onReload={takeDisk} onKeep={keepMine} /></div> : null}
          {offer ? (
            <div className="m-drop">
              <NoticeBanner message="A newer local draft exists for this task."
                actions={[
                  { label: "Restore it", onClick: restore },
                  { label: "Discard", onClick: discard },
                ]} />
            </div>
          ) : null}
          {notice("editor")}
          {nudge && !nudgeOff && !passed ? (
            <div style={{ position: "fixed", right: 24, left: narrow ? 24 : undefined, bottom: 24, zIndex: 30 }}>
              <StuckNudge minutes={Math.round(active / 60)} hintsShown={hints.shown.length} hintsTotal={hints.total} hintReady={hintReady}
                onHint={() => { setNudgeOff(true); hint(); }} onBury={buryAndLeave} onDismiss={() => setNudgeOff(true)} />
            </div>
          ) : null}
          {task.has_given ? <NoticeBanner message="This task ships given code above solve() — read it, but leave it alone." actions={[]} /> : null}

          <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
            {/* Run executes and grades nothing; Submit is the committing act, so it is the
              * one primary in the row and the only one that costs an attempt */}
            <Button variant="secondary" kbdHint="Ctrl/⌘+Enter" onClick={run} disabled={!!inflight || passed}>
              {inflight === "run" ? "Running…" : "Run"}
            </Button>
            <Button kbdHint="Ctrl/⌘+⇧+Enter" onClick={submit} disabled={!!inflight || passed}>
              {inflight === "submit" ? "Submitting…" : "Submit"}
            </Button>
            <Timer seconds={active} paused={!hasAttempt || passed} />
            <span className="tabular" style={{ fontSize: 13, color: "var(--text-muted)" }}>
              {runNo ? `attempt ${runNo}` : "not started"}
            </span>
            {attempt ? <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 12.5, color: "var(--text-faint)" }}>seed {attempt.seed}</span> : null}
            <div style={{ flex: 1 }} />
            {dirty || syntaxBad ? (
              <span style={{ fontSize: 12.5, color: syntaxBad ? "var(--warn)" : "var(--text-faint)" }}>
                ● {syntaxBad ? "not saved — syntax" : "unsaved"}
              </span>
            ) : null}
            {hasAttempt && !passed ? <Button variant="quiet" onClick={abandon} style={{ fontSize: 13 }}>Abandon</Button> : null}
            {passed ? null : (
              <Button variant="quiet" onClick={bury} style={{ fontSize: 13 }}>
                {task.buried ? "Unbury" : "Bury for today"}
              </Button>
            )}
          </div>

          <Editor value={code} onChange={edit} onRun={run} onSubmit={submit} readOnly={passed} dark={dark} height={narrow ? "60vh" : "calc(100vh - 364px)"} />

          <Card label={ungraded ? "Output · your run" : resultNo ? `Result · attempt ${resultNo}` : "Result"} padding={16}>
            {/* the region stays mounted and only the banner inside it is keyed: a live region
              * that arrives with its text already in place is never announced */}
            <div role="status">
              <div className="m-rise" key={result.state}>
                {result.state === "ran" ? (
                  <div style={{ borderRadius: "var(--radius)", padding: "12px 16px", fontSize: 14, background: "var(--pass-bg)", borderLeft: "3px solid var(--pass)" }}>
                    <span style={{ fontWeight: 600, color: "var(--pass)", letterSpacing: ".04em" }}>✓ TESTS PASS</span>
                    <span style={{ marginLeft: 10, fontSize: 13, color: "var(--text-muted)" }}>
                      nothing graded and no attempt used — Submit when you want it to count
                    </span>
                  </div>
                ) : (
                  <ResultBanner
                    state={result.state}
                    headline={result.state === "failed" ? result.headline : undefined}
                    gradeLine={passed ? `${result.grade.toUpperCase()} · ${secs(active)} · ${plural(result.attempts, "attempt")} · box ${result.box + 1} of ${task.ladder.length}` : undefined}
                    backIn={passed ? plural(result.dueIn, "day") : undefined} />
                )}
              </div>
            </div>

            {(result.state === "failed" || result.state === "ran") && result.output ? (
              <Collapsible label="Full output" meta={`pytest · ${plural(result.output.trimEnd().split("\n").length, "line")}`} style={{ marginTop: 8 }}>
                {result.output}
              </Collapsible>
            ) : null}

            {passed && result.reason ? (
              <div style={{ ...ASIDE, marginTop: 8 }}>Why {result.grade}: {result.reason}.</div>
            ) : null}

            {passed ? (
              <div style={{ marginTop: 10, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
                {/* the climb animation would read as a promotion on a card that just fell */}
                <span className={result.stepped ? (fell ? "m-fade" : "m-step") : undefined} style={{ display: "inline-flex" }}><LadderMeter box={result.box + 1} intervals={task.ladder} /></span>
                <span style={{ fontSize: 13, color: "var(--text-muted)" }}>
                  {stepLine(result.grade, result.box, result.fromBox, result.stepped, task.ladder.length)} — code archived, stub restored for next time
                </span>
                <div style={{ flex: 1 }} />
                <Button variant="quiet" onClick={() => { location.hash = "#/"; }}>Back to Today</Button>
                {nextSlug ? (
                  <Button variant="secondary" onClick={() => { location.hash = `#/task/${encodeURIComponent(nextSlug)}`; }}>Next in Today →</Button>
                ) : null}
              </div>
            ) : null}
          </Card>
        </div>
      </div>
    </div>
  );
}
