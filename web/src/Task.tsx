import { useCallback, useEffect, useRef, useState } from "react";
import { Button, Card, Collapsible, ConflictBanner, EmptyState, LadderMeter, NoticeBanner, ResultBanner, SpecText, StatusBadge, TagChip, Timer } from "./ds/index.js";
import { ApiError, api, post, type Task as TaskData, type RunResult } from "./api";
import { Editor } from "./Editor";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)" };
const ASIDE = { fontSize: 12.5, color: "var(--text-faint)" };
const PLAIN = { fontWeight: 400, textTransform: "none" as const, letterSpacing: 0, ...ASIDE };
const AUTOSAVE_MS = 800;
const ATTEMPT_MS = 5000;    // reading the task is work: the clock starts once the page settles
const HEARTBEAT_MS = 60_000;
// long enough for `role="status"` to finish speaking the message before the node goes
const GATE_MS = 4000;
const draftKey = (slug: string) => `drillion-draft-${slug}`;
const secs = (n: number) => n >= 60 ? `${Math.floor(n / 60)}m${String(n % 60).padStart(2, "0")}s` : `${n}s`;
const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

/** A refused action, shown beside the control that asked for it. */
type Gate = { at: "hints" | "solution" | "editor" | "note"; message: string } | null;

/** The optimistic lock's 409, or null for any other failure. */
const conflictOf = ({ status, detail }: ApiError) =>
  status === 409 && detail?.etag !== undefined && detail.code !== undefined
    ? { etag: detail.etag, code: detail.code }
    : null;

type Result =
  | { state: "idle" | "running" }
  | { state: "failed"; attempts: number; headline: string; output: string }
  | { state: "passed"; grade: string; box: number; stepped: boolean; fromBox: number; reason: string; dueIn: number; attempts: number; code: string };

/** The pass banner's one line about the card: `stepped` is the server's answer to whether
 *  the card moved, and `box` against `fromBox` says which way. */
export function stepLine(grade: string, box: number, fromBox: number, stepped: boolean, boxes: number) {
  if (stepped) return box < fromBox ? "the card stepped back a box — it comes back sooner" : "the card stepped up";
  if (box === boxes - 1) return "the card is already in the top box and stays there";
  if (box === 0) return "the card is already in the first box and stays there";
  return `${grade} keeps the card where it is`;
}

export function Task({ slug, dark }: { slug: string; dark: boolean }) {
  const [task, setTask] = useState<TaskData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [dirty, setDirty] = useState(false);
  const [syntaxBad, setSyntaxBad] = useState(false);
  const [result, setResult] = useState<Result>({ state: "idle" });
  const [conflict, setConflict] = useState<{ etag: string; code: string } | null>(null);
  const [draftOffer, setDraftOffer] = useState<string | null>(null);
  const [gate, setGate] = useState<Gate>(null);
  const [active, setActive] = useState(0);
  const [nextHintIn, setNextHintIn] = useState<number | null>(null);
  const [nextSlug, setNextSlug] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);          // a hint spent twice cannot be un-spent
  const [nudge, setNudge] = useState(false);        // the server's offer of a hint, not ours
  const [nudgeOff, setNudgeOff] = useState(false);
  const [note, setNote] = useState("");
  const [noteDirty, setNoteDirty] = useState(false);

  // Refs carry the live values into the async chain; state alone would capture a stale closure.
  const codeRef = useRef(""), etagRef = useRef(""), dirtyRef = useRef(false);
  const noteRef = useRef(""), noteDirtyRef = useRef(false);
  const timer = useRef<number | undefined>(undefined);
  const noteTimer = useRef<number | undefined>(undefined);
  const gateTimer = useRef<number | undefined>(undefined);
  const inflight = useRef<Promise<void> | null>(null);
  const attemptRef = useRef(false);
  const opening = useRef<Promise<void> | null>(null);
  const dropped = useRef(false);             // discarded here: do not re-open the attempt behind them
  const hasAttempt = !!task?.attempt;
  const passed = result.state === "passed";

  const adopt = useCallback((p: TaskData, keepCode = false) => {
    setTask(p); etagRef.current = p.etag; attemptRef.current = !!p.attempt;
    setActive(p.attempt?.active ?? 0);
    setNextHintIn(p.hints.next_in);
    setNudge(p.nudge);
    // a note half typed when the attempt opens itself must not be replaced by the server's
    if (!noteDirtyRef.current) { setNote(p.note); noteRef.current = p.note; }
    if (!keepCode) { setCode(p.code); codeRef.current = p.code; setDirty(false); dirtyRef.current = false; }
  }, []);

  /** A notice that says one thing and gets out of the way — the hint gate's whole UI. */
  const flash = useCallback((message: string) => {
    setGate({ at: "hints", message });
    clearTimeout(gateTimer.current);
    gateTimer.current = setTimeout(() => setGate(null), GATE_MS);
  }, []);

  // load, and offer a newer local draft over what the file holds
  useEffect(() => {
    let live = true;
    setTask(null); attemptRef.current = false; dropped.current = false; setError(null); setResult({ state: "idle" }); setConflict(null); setGate(null); setNextSlug(null); setNudgeOff(false);
    setNote(""); noteRef.current = ""; noteDirtyRef.current = false; setNoteDirty(false);
    api<TaskData>(`/task/${encodeURIComponent(slug)}`).then((p) => {
      if (!live) return;
      adopt(p);
      try {
        const saved = JSON.parse(localStorage.getItem(draftKey(slug)) || "null");
        if (saved && saved.etag === p.etag && saved.code !== p.code) setDraftOffer(saved.code);
        else setDraftOffer(null);
      } catch { setDraftOffer(null); }
    }).catch((e) => live && setError(e.message));
    return () => { live = false; };
  }, [slug, adopt]);

  /** An attempt must exist before the server will accept an edit, a run or a hint.
   * Concurrent callers share one POST — the debounced save and Run can arrive together. */
  const ensureOpen = useCallback(async () => {
    if (attemptRef.current) return;
    if (!opening.current) {
      opening.current = post<TaskData>(`/task/${encodeURIComponent(slug)}/open`)
        .then((p) => { adopt(p, dirtyRef.current); })          // never clobber text already typed
        .finally(() => { opening.current = null; });
    }
    await opening.current;
  }, [slug, adopt]);

  const flush = useCallback(async () => {
    if (!dirtyRef.current || !etagRef.current) return;
    const sent = codeRef.current;
    try {
      await ensureOpen();                  // typing is starting work; the PUT 409s without this
      const r = await api<{ etag: string }>(`/task/${encodeURIComponent(slug)}`, {
        method: "PUT", body: JSON.stringify({ code: sent, etag: etagRef.current }),
      });
      etagRef.current = r.etag;
      setSyntaxBad(false);
      if (codeRef.current === sent) { dirtyRef.current = false; setDirty(false); }
    } catch (e) {
      // never rethrow: `edit()` fires this unawaited and `run()` awaits it
      if (!(e instanceof ApiError)) { setGate({ at: "editor", message: `could not save — ${(e as Error).message}` }); return; }
      const clash = conflictOf(e);
      if (e.status === 400) setSyntaxBad(true);                       // silent: an amber dot, no banner
      else if (clash) setConflict(clash);
      else if (e.status === 409) setGate({ at: "editor", message: e.detail?.error ?? e.message }); // no open attempt
      else setGate({ at: "editor", message: e.message });
    }
  }, [slug, ensureOpen]);

  /** The note's save: debounce, then one PUT. No etag and no attempt to open — one note,
   * last write wins. */
  const saveNote = useCallback(async (text: string) => {
    try {
      await api(`/task/${encodeURIComponent(slug)}/note`, { method: "PUT", body: JSON.stringify({ text }) });
      if (noteRef.current === text) { noteDirtyRef.current = false; setNoteDirty(false); }
    } catch (e) {
      setGate({ at: "note", message: `note not saved — ${(e as Error).message}` });
    }
  }, [slug]);

  const editNote = (next: string) => {
    setNote(next); noteRef.current = next;
    noteDirtyRef.current = true; setNoteDirty(true);
    clearTimeout(noteTimer.current);
    noteTimer.current = setTimeout(() => saveNote(next), AUTOSAVE_MS);
  };

  // the page opens its own attempt once it has sat open; the delay skips a mis-click
  useEffect(() => {
    if (!task || hasAttempt || passed || dropped.current) return;
    const t = setTimeout(() => { ensureOpen().catch(() => {}); }, ATTEMPT_MS);
    return () => clearTimeout(t);
  }, [task, hasAttempt, passed, ensureOpen]);

  const edit = (next: string) => {
    setCode(next); codeRef.current = next;
    dirtyRef.current = true; setDirty(true);
    localStorage.setItem(draftKey(slug), JSON.stringify({ code: next, etag: etagRef.current }));
    clearTimeout(timer.current);
    timer.current = setTimeout(() => { inflight.current = flush(); }, AUTOSAVE_MS);
  };

  useEffect(() => () => {
    clearTimeout(timer.current); clearTimeout(gateTimer.current); clearTimeout(noteTimer.current);
    if (noteDirtyRef.current) saveNote(noteRef.current);   // leaving mid-debounce must not eat it
  }, [slug, saveNote]);

  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => { if (dirtyRef.current || noteDirtyRef.current) e.preventDefault(); };
    addEventListener("beforeunload", warn);
    return () => removeEventListener("beforeunload", warn);
  }, []);

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

  const run = async () => {
    clearTimeout(timer.current);
    setResult({ state: "running" });
    try {
      await inflight.current;              // ride the etag the pending PUT returns
      await ensureOpen();
      const r = await post<RunResult>(`/task/${encodeURIComponent(slug)}/run`, { code: codeRef.current, etag: etagRef.current });
      etagRef.current = r.etag;
      dirtyRef.current = false; setDirty(false); setSyntaxBad(false);
      setNudge(false);                     // a run answers the nudge, whichever way it went
      if (r.passed) {
        localStorage.removeItem(draftKey(slug));
        setResult({ state: "passed", grade: r.grade, box: r.box, stepped: r.stepped, fromBox: r.from_box, reason: r.reason, dueIn: r.due_in, attempts: r.attempts, code: r.code });
        setCode(r.code);
        setTask((p) => p && ({ ...p, reference: r.reference, lapses: r.lapses }));
        setNextSlug(r.next);
      } else {
        setResult({ state: "failed", attempts: r.attempts, headline: r.headline.join("\n") || "The tests did not pass.", output: r.output });
        setTask((p) => p && p.attempt ? { ...p, attempt: { ...p.attempt, attempts: r.attempts } } : p);
      }
    } catch (e) {
      const err = e as ApiError, clash = conflictOf(err);
      if (clash) { setConflict(clash); setResult({ state: "idle" }); }
      else if (err.status === 400) { setSyntaxBad(true); setResult({ state: "failed", attempts: 0, headline: `${err.detail?.error} (line ${err.detail?.line})`, output: "" }); }
      else { setResult({ state: "failed", attempts: 0, headline: err.message, output: "" }); }
    }
  };

  const hint = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await inflight.current;              // the payload carries an etag: never over a live PUT
      await ensureOpen();
      adopt(await post<TaskData>(`/task/${encodeURIComponent(slug)}/hint`), dirtyRef.current);
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
      await inflight.current;              // the payload carries an etag: never over a live PUT
      await ensureOpen();
      adopt(await post<TaskData>(`/task/${encodeURIComponent(slug)}/solution`), dirtyRef.current);
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
    clearTimeout(timer.current);
    await inflight.current;
    try {
      const p = await post<TaskData>(`/task/${encodeURIComponent(slug)}/abandon`, { etag: etagRef.current });
      localStorage.removeItem(draftKey(slug));
      dropped.current = true;
      adopt(p); setResult({ state: "idle" }); setGate(null); setNextSlug(null);
    } catch (e) {
      const err = e as ApiError, clash = conflictOf(err);
      if (clash) setConflict(clash); else setGate({ at: "editor", message: err.message });
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

  const takeDisk = () => {
    if (!conflict) return;
    etagRef.current = conflict.etag;
    setCode(conflict.code); codeRef.current = conflict.code;
    dirtyRef.current = false; setDirty(false);
    localStorage.removeItem(draftKey(slug));
    setConflict(null);
  };
  const keepMine = () => {
    if (!conflict) return;
    etagRef.current = conflict.etag;          // adopt the disk version's etag, then overwrite with ours
    dirtyRef.current = true; setDirty(true);
    setConflict(null);
    inflight.current = flush();
  };

  if (error) return <EmptyState message={`Could not load ${slug}: ${error}`} actionLabel="Back to Today" onAction={() => { location.hash = "#/"; }} />;
  if (!task) return <EmptyState message="Loading…" />;

  const { meta, hints, solution: gateState, attempt, reference } = task;
  const hintsLeft = hints.total - hints.shown.length;
  const hintReady = nextHintIn === null || nextHintIn <= 0;
  /** Peeked this sitting or earned by passing; `solution_shown` survives a reload, and still costs. */
  const peeked = !!attempt?.solution_shown;
  const flagged = task.lapses >= task.lapse_limit;
  /** The gate banner, under the control that raised it. The container stays in the tree so
   * screen readers have a live region to announce into. */
  const notice = (at: Exclude<Gate, null>["at"]) => (
    <div role="status" style={{ marginTop: gate?.at === at ? 10 : 0 }}>
      {gate?.at === at ? <div className="m-drop"><NoticeBanner message={gate.message} actions={[{ label: "Dismiss", onClick: () => setGate(null) }]} /></div> : null}
    </div>
  );

  const runNo = passed ? result.attempts : attempt ? attempt.attempts + 1 : 0;   // the run you are on
  const resultNo = "attempts" in result ? result.attempts : 0;                   // the run this result came from
  const fell = passed && result.stepped && result.box < result.fromBox;

  return (
    <div style={{ maxWidth: 1500, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 14 }}>
        <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-faint)" }}>{meta.topic}</span>
        <h1 style={{ margin: 0, fontSize: "var(--fs-h)", fontWeight: 600 }}>{meta.title}</h1>
        <StatusBadge status={task.status} />
        <StatusBadge status={meta.difficulty} />
        <div style={{ flex: 1 }} />
        {meta.track ? <TagChip label={meta.track} small /> : null}
        <span title={`${meta.tier}/${meta.tags.join(" ")}`} style={{ fontFamily: "var(--font-mono)", fontSize: 12.5 }}>
          <span style={{ color: "var(--text-faint)" }}>{meta.tier}/</span>
          <span style={{ color: "var(--text-muted)" }}>{meta.tags.join(" · ")}</span>
        </span>
        {meta.source ? <span style={ASIDE}>{meta.source}</span> : null}
      </div>

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        <div style={{ width: "42%", minWidth: 340, maxWidth: "70%", maxHeight: "calc(100vh - 148px)", overflow: "auto", resize: "horizontal" }}>
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
                    : <div style={ASIDE}>The reference answer, for comparison with what you wrote. It closes again when this card comes back.</div>}
                  <SpecText text={"```python\n" + reference + "\n```"} slug={slug} />
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
              <div style={{ ...LABEL, marginBottom: 10 }}>
                Note <span style={PLAIN}>· {noteDirty ? "unsaved" : "yours, kept with the task"}</span>
              </div>
              {/* ds/ has no multi-line field: plain element, DS tokens, the browser's focus ring */}
              <textarea value={note} onChange={(e) => editNote(e.target.value)} rows={3}
                aria-label={`Your note on ${meta.title}`}
                placeholder="What caught you out? Write it down while you still remember."
                style={{ width: "100%", boxSizing: "border-box", resize: "vertical", display: "block",
                  fontFamily: "var(--font-sans)", fontSize: 14, lineHeight: 1.55, padding: "8px 12px",
                  borderRadius: "var(--radius)", border: "1px solid var(--border-strong)",
                  background: "var(--surface-2)", color: "var(--text)" }} />
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

        <div style={{ flex: 1, minWidth: 420, display: "grid", gap: 12 }}>
          {conflict ? <div className="m-drop"><ConflictBanner detail="Your draft and the file on disk have diverged." onReload={takeDisk} onKeep={keepMine} /></div> : null}
          {draftOffer ? (
            <div className="m-drop">
              <NoticeBanner message="A newer local draft exists for this task."
                actions={[
                  { label: "Restore it", onClick: () => { edit(draftOffer); setDraftOffer(null); } },
                  { label: "Discard", onClick: () => { localStorage.removeItem(draftKey(slug)); setDraftOffer(null); } },
                ]} />
            </div>
          ) : null}
          {notice("editor")}
          {nudge && !nudgeOff && !passed ? (
            <div className="m-drop">
              <NoticeBanner message="Half an hour on this and nothing run yet — a hint is not cheating. You cannot work out something nobody has told you about."
                actions={[{ label: `Show hint ${hints.shown.length + 1}`, onClick: hint }, { label: "Not now", onClick: () => setNudgeOff(true) }]} />
            </div>
          ) : null}
          {task.has_given ? <NoticeBanner message="This task ships given code above solve() — read it, but leave it alone." actions={[]} /> : null}

          <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
            <Button kbdHint="Ctrl+Enter" onClick={run} disabled={result.state === "running" || passed}>
              {result.state === "running" ? "Running…" : "Run tests"}
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

          <Editor value={code} onChange={edit} onRun={run} readOnly={passed} dark={dark} height="calc(100vh - 364px)" />

          <Card label={resultNo ? `Result · attempt ${resultNo}` : "Result"} padding={16}>
            {/* the region stays mounted and only the banner inside it is keyed: a live region
              * that arrives with its text already in place is never announced */}
            <div role="status">
              <div className="m-rise" key={result.state}>
                <ResultBanner
                  state={result.state}
                  headline={result.state === "failed" ? result.headline : undefined}
                  gradeLine={passed ? `${result.grade.toUpperCase()} · ${secs(active)} · ${plural(result.attempts, "attempt")} · box ${result.box + 1} of ${task.ladder.length}` : undefined}
                  backIn={passed ? plural(result.dueIn, "day") : undefined} />
              </div>
            </div>

            {result.state === "failed" && result.output ? (
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
