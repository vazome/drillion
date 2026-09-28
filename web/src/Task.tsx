import { memo, useCallback, useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import { Button, Icon, Collapsible, ConflictBanner, EmptyState, FailedCase, Kbd, NoteField, GraceNotice, NoticeBanner, RequiresTag, RowFlags, SpecText, StatusBadge, TaskPath, Terminal, Timer, StuckNudge } from "./ds/index.js";
import { ApiError, api, post, resetRepo, type Task as TaskData, type RunResult, type Case, type Diagnostic } from "./api";
import { depsHref, prefetch, taskHref } from "./Deps";
import { plural, secs, topicNo } from "./format";
import { strength } from "./strength";
import { DiffView, Editor } from "./Editor";
import { ChartFiles, ManifestFailure } from "./ManifestWorkspace";
import { useDraft } from "./useDraft";
import { fontStack, setPrefs, usePrefs, type Prefs } from "./prefs";
import { resultBounds, Splitter, TaskPanes } from "./TaskPanes";
import { Crumbs } from "./Shell";
import { useNarrow } from "./narrow";
import { Level } from "./Level";
import { Climb, CLIMB } from "./Climb";
import { Drop, Swap } from "./motion";
import css from "./Task.module.css";

const ATTEMPT_MS = 5000;    // reading the task is work: the clock starts once the page settles
const HEARTBEAT_MS = 60_000;
// long enough for `role="status"` to finish speaking the message before the node goes
const GATE_MS = 4000;
const HINT_TEXT = { fontSize: 14 };
/** The shortcut's modifier as this keyboard labels it. */
const MOD = /Mac|iPhone|iPad/.test(navigator.platform) ? "⌘" : "Ctrl";
/** `0:48`, the way the hint countdown reads. */
const clockOf = (n: number) => `${Math.floor(n / 60)}:${String(n % 60).padStart(2, "0")}`;
/** The page re-renders every second while the clock runs; Markdown is only re-parsed when
 *  its text changes. */
const Spec = memo(SpecText);
/** A reference shown with nothing of the learner's to diff against, highlighted as its file. */
const FENCE: Record<TaskData["meta"]["kind"], string> = { python: "python", docker: "dockerfile", manifest: "yaml", helm: "yaml", sql: "sql", git: "shell" };

/** A refused action, shown beside the control that asked for it. */
type Gate = { at: "hints" | "solution" | "editor" | "note"; message: string } | null;

/** `ran` is an ungraded Run that came back green: the tests pass, nothing moved. Only
 *  `passed` is a graded pass, and only it ends the attempt. */
type Result =
  | { state: "idle" | "running" }
  | { state: "ran"; output: string; printed: string; rendered: string }
  | { state: "failed"; graded: boolean; attempts: number; headline: string; output: string; printed: string; case: Case | null; diagnostics: Diagnostic[]; rendered: string }
  | { state: "passed"; grade: string; box: number; stepped: boolean; fromBox: number; reason: string; dueIn: number; attempts: number; code: string };

/** The pass banner's one line about where the task now sits: `stepped` is the server's answer
 *  to whether it moved, and `box` against `fromBox` says which way. */
export function stepLine(grade: string, box: number, fromBox: number, stepped: boolean, boxes: number) {
  if (stepped) return box < fromBox ? "it comes back sooner than last time" : "it comes back later than last time";
  if (box === boxes - 1) return "it is as far out as it goes and stays there";
  if (box === 0) return "it is as close in as it goes and stays there";
  return `${grade} leaves it where it is`;
}

/** After a pass the editor pane becomes this: yours against the reference. The changed lines
 *  are marked in the accent, never red and green, because both versions passed. */
function Review({ kind, mine, reference, dark, prefs, narrow }: {
  kind: TaskData["meta"]["kind"]; mine: string; reference: string; dark: boolean; prefs: Prefs; narrow: boolean;
}) {
  const [view, setView] = useState<"compare" | "yours" | "reference">("compare");
  const [inline, setInline] = useState(false);
  const [changed, setChanged] = useState<number | null>(null);
  const side = !inline && !narrow;       // side by side needs the width: below 1100px it is inline
  const shown = view === "yours" ? mine : reference;
  return (
    <section aria-label="Review" className={css.review}>
      <div className={css.reviewBar}>
        <span className={css.label}>Review</span>
        <div role="group" aria-label="Show" className={css.segment}>
          {(["compare", "yours", "reference"] as const).map((k) => (
            <button key={k} type="button" aria-pressed={view === k} onClick={() => setView(k)}>{cap(k)}</button>
          ))}
        </div>
        {changed === null ? null : <span className={css.aside}>{changed ? `${changed} ${changed === 1 ? "line differs" : "lines differ"}` : "the same"}</span>}
        <span className={css.grow} />
        {view === "compare" && !narrow ? (
          <div role="group" aria-label="Layout" className={css.segment}>
            <button type="button" aria-pressed={!inline} onClick={() => setInline(false)}>Side by side</button>
            <button type="button" aria-pressed={inline} onClick={() => setInline(true)}>Inline</button>
          </div>
        ) : null}
      </div>
      {view === "compare" && side ? (
        <div className={css.sides}>
          <span><strong>Yours</strong></span>
          <span><strong>Reference</strong></span>
        </div>
      ) : null}
      <div className={css.editorBox}>
        <div className={css.fill}>
          {view === "compare"
            ? <DiffView kind={kind} mine={mine} reference={reference} dark={dark} maxHeight="100%" prefs={prefs} sideBySide={side} onChanges={setChanged} unframed />
            : <pre tabIndex={0} aria-label={view === "yours" ? "Your passing code" : "The reference"} className={css.code}>
                {shown.replace(/\n$/, "").split("\n").map((line, i) => <span key={i}>{line}{"\n"}</span>)}
              </pre>}
        </div>
      </div>
    </section>
  );
}

/** What the learner is checking, by kind: the idle and running lines name it. */
const FILE: Record<TaskData["meta"]["kind"], string> = { python: "code", docker: "Dockerfile", manifest: "manifest", helm: "chart", sql: "SQL", git: "repository" };
const CHECKS: Record<TaskData["meta"]["kind"], string> = {
  python: "pytest, on freshly generated data.",
  docker: "hadolint, then the build context, then the rules.",
  manifest: "the Kubernetes schema, offline, then the rules.",
  helm: "Helm renders the chart, then the schema and the rules.",
  sql: "Postgres runs it on this sitting's data and on a hidden second dataset, then the rules.",
  git: "git compares your repository with the answer key's: every branch, HEAD, the staging area, and origin.",
};
/** The tabs around the editor, named for what they hold. A Helm chart keeps the default words. */
const TABS: Partial<Record<TaskData["meta"]["kind"], { label: string; partOf: string }>> = {
  docker: { label: "Build context files", partOf: "the build context" },
  sql: { label: "Database files", partOf: "the database" },
};

/** The first lines of the result panel: what happened, and what it cost. A Run never costs
 *  an attempt or moves the card, and says so whichever way it went. */
function Outcome({ result, kind, active, ladder, flagged, lapses }: {
  result: Result; kind: TaskData["meta"]["kind"]; active: number; ladder: number[]; flagged: boolean; lapses: number;
}) {
  const rules = kind === "python" ? "test" : "rule";
  switch (result.state) {
    case "idle": return (
      <div className={css.state}>
        <strong>Nothing run yet.</strong>
        <p className={css.aside}>Run checks your {FILE[kind]} and costs nothing. Submit is the one that grades it and moves the card.</p>
        <p className={css.keys}>{kind !== "git" && <span>Run <Kbd>{MOD} ↵</Kbd></span>}<span>Submit <Kbd>{MOD} ⇧ ↵</Kbd></span></p>
      </div>
    );
    case "running": return (
      <div className={css.state}>
        <strong>Checking your {FILE[kind]}…</strong>
        <p className={css.aside}>{cap(CHECKS[kind])}</p>
      </div>
    );
    case "ran": return (
      <div className={css.state}>
        <strong className={css.ok}><Icon name="CheckmarkOutline" />Every {rules} {kind === "python" ? "passed" : "met"} on this Run</strong>
        <p className={css.aside}>Nothing was graded and no attempt was used. Submit when you are ready to count it.</p>
      </div>
    );
    case "failed": {
      const n = result.diagnostics.length;
      return (
        <div className={css.state}>
          <span className={css.verdict}>
            <span className={css.fail}><Icon name="CloseOutline" size={14} />{result.graded ? "Not yet" : n ? `${plural(n, rules)} not met` : "Not passing yet"}</span>
            <span className={css.aside}>{result.graded
              ? `${result.attempts ? `Submit ${result.attempts} · ` : ""}the card has not moved`
              : "Run, so no attempt used and nothing on the ladder moved."}</span>
          </span>
          {kind === "python" || !n ? <p className={css.headline}>{result.headline}</p> : null}
        </div>
      );
    }
    case "passed": {
      const fell = result.stepped && result.box < result.fromBox;
      const word = strength(result.box, true, ladder)!;
      return (
        <div className={css.passed} data-grade={result.grade}>
          <p className={css.gradeLine}><span>PASSED · {result.grade.toUpperCase()}</span> · {secs(active)} · {plural(result.attempts, "attempt")}</p>
          <p className={css.climb}>
            {/* the step animation would read as a promotion on a task that just fell back; it
              * waits for the climb below to land */}
            {fell ? null : <span className={result.stepped ? "m-step" : undefined} style={result.stepped ? CLIMBED : undefined}><Level of={word} /></span>}
            <span className={css.aside}>{fell ? "It comes back sooner, so it gets another look while it is fresh."
              : cap(stepLine(result.grade, result.box, result.fromBox, result.stepped, ladder.length)) + "."}</span>
          </p>
          <Climb ladder={ladder} from={result.fromBox} to={result.box} />
          {flagged ? (
            <p className={css.flag}><Icon name="WarningAlt" />You have struggled with this {plural(lapses, "time")}. The hints or the prereqs may be the problem, not you.</p>
          ) : null}
        </div>
      );
    }
  }
}

/** The strength word steps once the climb has landed. */
const CLIMBED = { animationDelay: `${CLIMB.wait + CLIMB.move}ms` };

const cap = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

/** The task's header, on one line: number and title, what it is, what it needs, the clock.
 *  Needs chips drop their titles past two, or past a 30-character one; the title stays in the
 *  tooltip. What a task opens is on its lineage screen, one click from any Needs chip. */
function TaskHeader({ task, active, showTimer, paused, onAbandon }: {
  task: TaskData; active: number; showTimer: boolean; paused: boolean; onAbandon?: () => void;
}) {
  const { meta, requires } = task;
  const titles = requires.length <= 2 && requires.every((r) => r.title.length <= 30);
  return (
    <section aria-label="Task" className={css.header}>
      <div className={css.line}>
        <span className={css.num}>{topicNo(meta.topic)}</span>
        <h1 className={css.h1}>{meta.title}</h1>
        <Level of={meta.difficulty} />
        <TaskPath tier={meta.tier} track={meta.track} tags={meta.tags} />
        <span className={css.pill} data-status={task.status}>{task.status}</span>
        <RowFlags lapses={task.lapses} lapseLimit={task.lapse_limit} />
        {requires.length ? <>
          <span aria-hidden="true" className={css.rule} />
          <span className={css.needs}>Needs
            {requires.map((r) => (
              <RequiresTag key={r.slug} topic={r.topic} title={titles ? r.title : undefined}
                state={r.state} href={depsHref(r.slug)} onPointerEnter={() => { void prefetch(r.slug); }} />
            ))}
          </span>
        </> : null}
        <span className={css.grow} />
        {/* hidden by preference only: the clock behind it keeps running, and the grade is the same */}
        <span className={css.clock}>
          {showTimer ? <Timer seconds={active} paused={paused} /> : null}
          {onAbandon ? <button type="button" onClick={onAbandon} className={css.abandon}>Abandon</button> : null}
        </span>
      </div>
    </section>
  );
}

/** The output under the editor. Until its splitter is dragged it fits what it shows, up to 40%
 *  of the column; a drag fixes its height, and a double-click or Enter lets it fit again.
 *  `running` sweeps the whole pane while the checks are out, edge to edge. */
function ResultPane({ narrow, label, running, children }: { narrow: boolean; label: string; running: boolean; children: ReactNode }) {
  const { resultPanePercent } = usePrefs();
  const box = useRef<HTMLElement>(null);
  const id = useId();
  const [size, setSize] = useState({ column: 800, own: 0 });
  const [live, setLive] = useState<number | null>(null);
  useEffect(() => {
    const own = box.current;
    const column = own?.parentElement;
    if (!own || !column) return;
    const observer = new ResizeObserver(() => setSize({ column: column.clientHeight, own: own.offsetHeight }));
    observer.observe(column);
    observer.observe(own);
    return () => observer.disconnect();
  }, []);
  const { min, max } = resultBounds(size.column);
  const chosen = live ?? resultPanePercent;
  const value = Math.max(min, Math.min(max, chosen ?? size.own / size.column * 100));
  return (
    <>
      {narrow ? null : <Splitter orientation="horizontal" className={css.resultSplit} span={size.column}
        value={value} min={min} max={max} label="Output height" controls={id}
        title="Drag to resize. Double-click to fit the output again."
        onDrag={setLive} onCommit={(next) => setPrefs({ resultPanePercent: next })}
        onReset={() => setPrefs({ resultPanePercent: null })} />}
      <section id={id} ref={box} aria-label={label} className={running ? `${css.result} m-sweep` : css.result}
        style={narrow || chosen === null ? undefined : { flex: `0 1 ${value}%`, maxHeight: "none" }}>
        {children}
      </section>
    </>
  );
}

export function Task({ slug, dark, bar }: { slug: string; dark: boolean; bar: (crumbs: ReactNode) => ReactNode }) {
  const prefs = usePrefs();
  const [task, setTask] = useState<TaskData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Result>({ state: "idle" });
  const [gate, setGate] = useState<Gate>(null);
  const [active, setActive] = useState(0);
  const [grace, setGrace] = useState(0);           // the server's reading minute, ticked down locally
  const [readFirstOff, setReadFirstOff] = useState(false);
  const [nextHintIn, setNextHintIn] = useState<number | null>(null);
  const [nextSlug, setNextSlug] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);          // a hint spent twice cannot be un-spent
  const [nudge, setNudge] = useState(false);        // the server's offer of a hint, not ours
  const [nudgeOff, setNudgeOff] = useState(false);
  const [inflight, setInflight] = useState<"run" | "submit" | null>(null);
  const narrow = useNarrow();

  const graceRef = useRef(0);                // read inside the tick, so it is not a dep
  const gateTimer = useRef<number | undefined>(undefined);
  const lastHint = useRef<HTMLDivElement>(null);
  const dropped = useRef(false);             // discarded here: do not re-open the attempt behind them
  const hasAttempt = !!task?.attempt;
  const passed = result.state === "passed";
  const url = `/task/${encodeURIComponent(slug)}`;

  /** Everything a task payload says that is not the draft's business. */
  const onPayload = useCallback((p: TaskData) => {
    setTask(p);
    setActive(p.attempt?.active ?? 0);
    setGrace(p.attempt?.grace ?? 0);
    setNextHintIn(p.hints.next_in);
    setNudge(p.nudge);
  }, []);

  const onSaveError = useCallback((message: string, at: "editor" | "note" = "editor") => setGate({ at, message }), []);
  const { code, dirty, syntax, conflict, offer, note, noteDirty, adopt, reset, edit, editNote,
    landed, ensureOpen, current, pending, settle, takeDisk, keepMine, discard, restore, absorb } =
    useDraft(slug, onPayload, onSaveError);

  /** A notice that says one thing and gets out of the way: what a locked hint or solution
   *  answers when pressed. */
  const flash = useCallback((message: string, at: "hints" | "solution" = "hints") => {
    const mine: Gate = { at, message };
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
      if (document.visibilityState !== "visible") return;
      // the grace is the server's, and it holds `active` at rest until it is spent
      if (graceRef.current > 0) { setGrace((g) => g - 1); return; }
      setActive((s) => s + 1);
      setNextHintIn((n) => (n === null ? null : Math.max(0, n - 1)));
    }, 1000);
    const beat = setInterval(() => {
      if (document.visibilityState !== "visible") return;
      post<{ active: number; nudge: boolean; grace: number }>(`/task/${encodeURIComponent(slug)}/touch`)
        .then((r) => { setActive(r.active); setNudge(r.nudge); setGrace(r.grace); }).catch(() => {});
    }, HEARTBEAT_MS);
    return () => { clearInterval(tick); clearInterval(beat); };
  }, [hasAttempt, passed, slug]);

  useEffect(() => { graceRef.current = grace; }, [grace]);

  // a hint just revealed lands at the end of the spec, right above the bar that asked for it
  const shownHints = task?.hints.shown.length ?? 0;
  const seenHints = useRef(shownHints);
  useEffect(() => {
    if (shownHints > seenHints.current) lastHint.current?.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    seenHints.current = shownHints;
  }, [shownHints]);

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
      if (r.graded) setNudge(false);       // a submission answers the nudge; a Run does not
      if (r.passed && r.graded) {
        setResult({ state: "passed", grade: r.grade, box: r.box, stepped: r.stepped, fromBox: r.from_box, reason: r.reason, dueIn: r.due_in, attempts: r.attempts, code: r.code });
        setTask((p) => p && ({ ...p, reference: r.reference, lapses: r.lapses, status: "done", attempt: p.attempt && { ...p.attempt, attempts: r.attempts } }));
        setNextSlug(r.next);
      } else if (r.passed) {
        setResult({ state: "ran", output: r.output, printed: r.printed, rendered: r.rendered ?? "" });
      } else {
        setResult({ state: "failed", graded: r.graded, attempts: r.attempts, headline: r.headline.join("\n") || "The tests did not pass.", output: r.output, printed: r.printed, case: r.case, diagnostics: r.diagnostics, rendered: r.rendered ?? "" });
        setTask((p) => p && p.attempt ? { ...p, attempt: { ...p.attempt, attempts: r.attempts } } : p);
      }
    } catch (e) {
      const err = e as ApiError, bad = err.status === 400;
      if (absorb(err) && !bad) setResult({ state: "idle" });      // the conflict banner has it now
      else setResult({ state: "failed", graded: submit, attempts: 0, output: "", printed: "", case: null, diagnostics: [], rendered: "",
        headline: bad ? `${err.detail?.error}${err.detail?.line != null ? ` (line ${err.detail.line})` : ""}` : err.message });
    } finally { setInflight(null); }
  };
  const run = () => { void go(false); };
  const submit = () => { void go(true); };

  /** Hint and solution are the same spend: over no live PUT, inside an attempt, once. */
  const spend = async (what: "hint" | "solution", refused: (err: ApiError) => void) => {
    if (busy) return;
    setBusy(true);
    try {
      await pending();               // the payload carries an etag: never over a live PUT
      await ensureOpen();
      adopt(await post<TaskData>(`${url}/${what}`));
      setGate(null);
    } catch (e) {
      refused(e as ApiError);
    } finally { setBusy(false); }
  };

  const hint = () => spend("hint", (err) => {
    const wait = err.status === 423 ? err.detail?.wait_secs : 0;
    if (wait) {
      setNextHintIn(wait);
      flash(`Not yet — ${secs(wait)}. Keep working; hint ${(task?.hints.shown.length ?? 0) + 1} unlocks itself.`);
    } else setGate({ at: "hints", message: err.message });
  });

  const solution = () => spend("solution", (err) => {
    const d = err.detail ?? {};
    const owed = [
      d.need_attempts ? plural(d.need_attempts, "more submit") : null,
      d.need_secs ? `${secs(d.need_secs)} more work` : null,
    ].filter(Boolean);
    if (owed.length) flash(`Not yet: the solution opens after ${owed.join(" and ")}.`, "solution");
    else setGate({ at: "solution", message: err.message });
  });

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

  /** Reset repository lives in the terminal's own head, not the toolbar: the command history
   *  the terminal keeps is not something Run or Submit ever touch. */
  const onResetRepo = () => {
    if (confirm("Put the repository back as the task set it up? Your command history is kept.")) void resetRepo(slug);
  };

  /** A Helm run that named a line in the learner's own file marks it, as a syntax error does.
   *  Kept stable across the clock's ticks, since a new one redraws the editor's diagnostics. */
  const edits = task?.meta.edits;
  const problem = useMemo(() => {
    const named = result.state === "failed" ? result.diagnostics.find((d) => d.file === edits && d.line) : undefined;
    return syntax ?? (named ? { message: named.message, line: named.line! } : null);
  }, [syntax, result, edits]);

  if (error) return <>{bar(null)}<EmptyState message={`Could not load ${slug}: ${error}`} actionLabel="Back to Today" onAction={() => { location.hash = "#/"; }} /></>;
  if (!task) return <>{bar(null)}<EmptyState message="Loading…" /></>;

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
    <div role="status">
      <Drop style={{ marginTop: 10 }}>{gate?.at === at ? <NoticeBanner message={gate.message} actions={[{ label: "Dismiss", onClick: () => setGate(null) }]} /> : null}</Drop>
    </div>
  );

  // an ungraded Run cost no attempt, so the card must not number it as one
  const ungraded = result.state === "ran" || (result.state === "failed" && !result.graded);
  const resultNo = !ungraded && "attempts" in result ? result.attempts : 0;   // the attempt this result came from

  const chart = !!meta.edits && task.chart.length > 0;
  // a pass, this sitting or the last, with the reference open: the editor gives way to Review
  const review = !!reference && !!mine && !peeked;
  const editor = <Editor kind={meta.kind} value={code} onChange={edit} onRun={run} onSubmit={submit} readOnly={passed} dark={dark} prefs={prefs} problem={problem} height="100%" />;
  const rendered = result.state === "failed" || result.state === "ran" ? result.rendered : "";
  const submits = attempt?.attempts ?? 0;

  return (<>
    {bar(<Crumbs group={meta.track ?? meta.tier} topic={meta.topic} />)}
    <main className={`${css.page} m-rise`}>
      <TaskHeader task={task} active={active} showTimer={prefs.showTimer} paused={!hasAttempt || passed}
        onAbandon={hasAttempt && !passed ? abandon : undefined} />

      <TaskPanes narrow={narrow} fixed={review ? 440 : undefined}>
        <div className={css.brief}>
          <div className={css.read}>
            <Spec text={task.spec_md} slug={slug} hideTitle />

            {reference && !review ? (
              <div className={css.after}>
                <div className={css.label}>Solution</div>
                {peeked
                  ? <NoticeBanner message="Solution shown: this pass won’t move the task further out. It grades as struggled and comes back just as soon." actions={[]} />
                  : <p className={css.aside}>{mine
                      ? "Your solution on the left, the reference on the right. It closes again when this task comes back."
                      : "The reference answer, for comparison with what you wrote. It closes again when this task comes back."}</p>}
                {mine
                  ? <DiffView kind={meta.kind} mine={mine} reference={reference} dark={dark} maxHeight="46vh" prefs={prefs} />
                  : <Spec text={"```" + FENCE[meta.kind] + "\n" + reference + "\n```"} slug={slug} />}
              </div>
            ) : null}

            {task.archive.length ? (
              <Collapsible label={`Archive · ${plural(task.archive.length, "previous pass")}`} mono={false} className={css.after}>
                {task.archive.slice().reverse().map((a, i) => (
                  <div key={i} style={{ marginBottom: 8 }}>
                    <div style={{ display: "flex", gap: 10, alignItems: "center", fontSize: 13 }}>
                      <span className="tabular" style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>{a.date}</span>
                      <StatusBadge status={a.grade} />
                    </div>
                    {a.revision ? (
                      <div className="tabular" style={{ fontSize: 12.5, color: "var(--text-faint)", fontFamily: "var(--font-mono)" }}>
                        {a.python ? `Python ${a.python}` : a.hadolint ? `hadolint ${a.hadolint}` : a.pglite ? `PGlite ${a.pglite}` : a.git ? `git ${a.git}` : `kubeconform ${a.validator} · Kubernetes ${a.kubernetes}`} · seed {a.seed} · grader {a.revision}
                      </div>
                    ) : null}
                    {a.code ? <pre style={{ margin: "6px 0 0", fontSize: 12.5, whiteSpace: "pre-wrap", color: "var(--text-muted)" }}>{a.code}</pre> : null}
                  </div>
                ))}
              </Collapsible>
            ) : null}

            <div className={css.after}>
              <NoteField value={note} onChange={editNote} dirty={noteDirty}
                ariaLabel={`Your note on ${meta.title}`}
                placeholder="What caught you out? Write it down while you still remember." />
              {notice("note")}
            </div>

            {flagged || hints.shown.length ? (
              <div className={css.after}>
                {flagged ? (
                  <p className={css.aside}>
                    You have struggled with this {plural(task.lapses, "time")}. The hints below, or the
                    tasks it builds on, are the likelier problem, not you.
                  </p>
                ) : null}
                {hints.shown.map((text, i) => (
                  <div key={i} ref={i === hints.shown.length - 1 ? lastHint : undefined} className={`${css.hint} m-expand`}>
                    <div className={css.hintHead}><Icon name="Idea" size={14} />Hint {i + 1} of {hints.total}</div>
                    <Spec text={text} slug={slug} style={HINT_TEXT} />
                  </div>
                ))}
              </div>
            ) : null}
          </div>
          {notice("hints")}
          {notice("solution")}
          {review ? (
            <div className={css.stuck}>
              <span className={css.aside}><Icon name="Unlocked" size={14} />Solution open: you passed this one. It closes again when the task comes back.</span>
            </div>
          ) : <div role="group" aria-label="Help with this task" className={css.stuck}>
            <span className={css.aside}>Stuck?</span>
            {hintsLeft ? (
              <button type="button" onClick={hint} disabled={busy || passed} className={css.help}>
                <Icon name="Idea" />Hint {hints.shown.length + 1}
                {hintReady ? null : <span className={css.mono}>in {clockOf(nextHintIn!)}</span>}
              </button>
            ) : <span className={css.aside}>All {hints.total} hints shown</span>}
            {reference ? (
              <span className={css.aside}><Icon name="Unlocked" size={14} />{peeked ? "Solution shown: this attempt is marked." : "Solution open: you passed this one."}</span>
            ) : (
              <button type="button" onClick={solution} disabled={busy} className={css.help}
                title="Taking it means this pass won’t move the task further out">
                <Icon name={gateState.unlocked ? "Unlocked" : "Locked"} size={14} />Solution
              </button>
            )}
          </div>}
        </div>

        <div className={css.work}>
          <Drop>{conflict ? <ConflictBanner detail="Your draft and the file on disk have diverged." onReload={takeDisk} onKeep={keepMine} /> : null}</Drop>
          <Drop>{offer ? (
            <NoticeBanner message="A newer local draft exists for this task."
              actions={[
                { label: "Restore it", onClick: restore },
                { label: "Discard", onClick: discard },
              ]} />
          ) : null}</Drop>
          {notice("editor")}
          {task.has_given ? <NoticeBanner message="This task ships given code above solve(): read it, but leave it alone." actions={[]} /> : null}

          {/* after a pass the editor fades out and Review comes in where it was */}
          <Swap id={review ? "review" : "edit"} className={css.swap}>
          {review ? <Review kind={meta.kind} mine={mine} reference={reference!} dark={dark} prefs={prefs} narrow={narrow} /> : <>
          {/* first in the DOM and drawn below the editor: Tab reaches Run before it lands in Monaco,
            * where Tab only indents */}
          <div role="toolbar" aria-label="Grade your file" className={css.grading}>
            <span className={css.mono}>{meta.kind === "git" ? "" : `${plural(submits, "submit")}${attempt ? ` · seed ${attempt.seed}` : ""}`}</span>
            {/* the marker lives inside the spacer, which is allowed to shrink below its own
              * content: a status that appears while you type must not re-wrap the row and
              * push the editor down under the cursor */}
            <div className={css.marker}>
              {dirty || syntax ? (
                <span data-syntax={syntax ? "" : undefined} title={syntax ? syntax.message : undefined}>
                  {syntax ? <Icon name="WarningAlt" size={14} /> : <Icon name="CircleFill" size={8} />}{syntax
                    ? `syntax error${syntax.line != null ? ` on line ${syntax.line}` : ""}, not saved`
                    : "unsaved"}
                </span>
              ) : null}
            </div>
            {/* Run executes and grades nothing; Submit is the committing act, so it is the
              * one primary in the row and the only one that costs an attempt */}
            <Button variant="secondary" kbdHint={meta.kind === "git" ? undefined : `${MOD} ↵`} onClick={run} disabled={!!inflight || passed}>
              <Icon name="Play" />{inflight === "run" ? "Running…" : "Run"}
            </Button>
            <Button kbdHint={`${MOD} ⇧ ↵`} onClick={submit} disabled={!!inflight || passed}>
              <Icon name="Send" />{inflight === "submit" ? "Submitting…" : "Submit"}
            </Button>
          </div>

          {meta.kind === "git" ? (
            // it takes what the column has left, the way the editor does: a fixed height here
            // would spill past the Run and Submit row whenever the window is short
            <div style={{ flex: 1, minHeight: 0, overflow: "hidden" }} onKeyDown={(e) => {
              if (e.key === "Enter" && e.shiftKey && (e.ctrlKey || e.metaKey)) { e.preventDefault(); submit(); }
            }}>
              <Terminal key={slug} slug={slug} dark={dark} live={hasAttempt && !passed}
                fontFamily={fontStack(prefs.font)} fontSize={prefs.fontSize} screenReader={prefs.screenReader}
                idleNote={passed ? "Passed. The shell is closed; your repository was graded as you left it."
                                 : "No attempt is open. The last output stays here; the shell starts with the next attempt."}
                actions={hasAttempt && !passed
                  ? <Button variant="quiet" onClick={onResetRepo}><Icon name="Reset" size={14} />Reset repository</Button>
                  : undefined} />
            </div>
          ) : (
            <div className={css.editorBox}>
              <div className={css.fill}>
                {chart && meta.edits ? (
                  // keyed by task: a new task opens on the learner's own file
                  <ChartFiles key={slug} edits={meta.edits} chart={task.chart} labels={TABS[meta.kind]}
                    diagnostics={result.state === "failed" ? result.diagnostics : []}>
                    {editor}
                  </ChartFiles>
                ) : editor}
              </div>
            </div>
          )}
          </>}
          </Swap>

          {review && !passed ? null : <ResultPane narrow={narrow} running={result.state === "running"} label={ungraded ? "Output of your run" : resultNo ? `Result of submit ${resultNo}` : "Result"}>
            {/* the region stays mounted and only the state inside it is keyed: a live region
              * that arrives with its text already in place is never announced */}
            <div role="status">
              <div className={result.state === "running" ? undefined : "m-rise"} key={result.state}>
                <Outcome result={result} kind={meta.kind} active={active} ladder={task.ladder}
                  flagged={passed && flagged} lapses={task.lapses} />
              </div>
            </div>

            {meta.kind !== "python" && result.state === "failed" && result.diagnostics.length ? (
              <ManifestFailure diagnostics={result.diagnostics} kind={meta.kind} />
            ) : null}
            {meta.kind === "python" && result.state === "failed" && result.case ? <FailedCase case={result.case} /> : null}

            {/* the learner's own print() first, open: it is the one line of the report they wrote */}
            {(result.state === "failed" || result.state === "ran") && result.printed ? (
              <Collapsible label="What you printed" meta={plural(result.printed.split("\n").length, "line")} defaultOpen style={{ marginTop: 8 }}>
                {result.printed}
              </Collapsible>
            ) : null}

            {/* what Helm made of the chart, or what the SQL returned: the thing to read first, so it opens on a Run */}
            {rendered ? (
              <Collapsible label={meta.kind === "sql" ? "Your result" : "Rendered"} meta={`${meta.kind === "sql" ? "on the data shown" : "helm template"} · ${plural(rendered.trimEnd().split("\n").length, "line")}`} defaultOpen={ungraded} style={{ marginTop: 8 }}>
                {rendered}
              </Collapsible>
            ) : null}

            {(result.state === "failed" || result.state === "ran") && result.output ? (
              <Collapsible label={meta.kind === "python" ? "Full output" : meta.kind === "sql" ? "Expected result" : meta.kind === "git" ? "Your repository" : "Validator details"} meta={`${{ python: "pytest", docker: "hadolint", sql: "the answer key", git: "git log --graph" }[meta.kind as string] ?? "raw report"} · ${plural(result.output.trimEnd().split("\n").length, "line")}`} style={{ marginTop: 8 }}>
                {result.output}
              </Collapsible>
            ) : null}

            {passed ? (
              <div className={css.actions}>
                <span className={css.grow} />
                <Button variant="quiet" onClick={() => { location.hash = "#/"; }}>Back to Today</Button>
                {nextSlug ? <Button onClick={() => { location.hash = taskHref(nextSlug); }}>Next in Today<Icon name="ArrowRight" /></Button> : null}
              </div>
            ) : null}
          </ResultPane>}
        </div>
      </TaskPanes>

      {/* both rise in by themselves; these only see them out */}
      <Drop className={css.corner} y={6} enter={false}>{grace > 0 && !readFirstOff && !passed ? (
        <GraceNotice seconds={grace} onDismiss={() => setReadFirstOff(true)} />
      ) : null}</Drop>
      <Drop className={css.corner} y={6} enter={false}>{nudge && !nudgeOff && !passed ? (
        <StuckNudge minutes={Math.round(active / 60)} hintsShown={hints.shown.length} hintsTotal={hints.total} hintReady={hintReady}
          onHint={() => { setNudgeOff(true); hint(); }} onDismiss={() => setNudgeOff(true)} />
      ) : null}</Drop>
    </main>
  </>);
}
