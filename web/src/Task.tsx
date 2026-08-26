import { useCallback, useEffect, useRef, useState } from "react";
import { Button, Card, Collapsible, ConflictBanner, EmptyState, LadderMeter, NoticeBanner, ResultBanner, SpecText, StatusBadge, TagChip, Timer } from "./ds/index.js";
import { ApiError, api, post, type Catalogue, type Task as TaskData, type RunResult } from "./api";
import { Editor } from "./Editor";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)" };
const ASIDE = { fontSize: 12.5, color: "var(--text-faint)" };          // the faint line beside a section label
const PLAIN = { fontWeight: 400, textTransform: "none" as const, letterSpacing: 0, ...ASIDE };
const AUTOSAVE_MS = 800;
const HEARTBEAT_MS = 60_000;
const GATE_MS = 1400;                                                  // the hint gate says its piece, then leaves
const draftKey = (slug: string) => `drillion-draft-${slug}`;
const secs = (n: number) => n >= 60 ? `${Math.floor(n / 60)}m${String(n % 60).padStart(2, "0")}s` : `${n} s`;
const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

/** A refused action, shown beside the control that asked for it. */
type Gate = { at: "hints" | "solution" | "editor"; message: string } | null;

type Result =
  | { state: "idle" | "running" }
  | { state: "failed"; headline: string; output: string }
  | { state: "passed"; grade: string; box: number; dueIn: number; attempts: number; code: string };

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
  const [solutionCode, setSolutionCode] = useState<string | null>(null);
  const [active, setActive] = useState(0);
  const [nextHintIn, setNextHintIn] = useState<number | null>(null);
  const [nextSlug, setNextSlug] = useState<string | null>(null);

  // Refs carry the live values into the async chain; state alone would capture a stale closure.
  const codeRef = useRef(""), etagRef = useRef(""), dirtyRef = useRef(false);
  const timer = useRef<number | undefined>(undefined);
  const gateTimer = useRef<number | undefined>(undefined);
  const inflight = useRef<Promise<void> | null>(null);
  const hasAttempt = !!task?.attempt;
  const passed = result.state === "passed";

  const adopt = useCallback((p: TaskData, keepCode = false) => {
    setTask(p); etagRef.current = p.etag;
    setActive(p.attempt?.active ?? 0);
    setNextHintIn(p.hints.next_in);
    if (!keepCode) { setCode(p.code); codeRef.current = p.code; setDirty(false); dirtyRef.current = false; }
  }, []);

  /** A notice that says one thing and gets out of the way — the hint gate's whole UI. */
  const flash = useCallback((message: string) => {
    setGate({ at: "hints", message });
    clearTimeout(gateTimer.current);
    gateTimer.current = setTimeout(() => setGate(null), GATE_MS);
  }, []);

  // ---- load, and offer a newer local draft over what the file holds
  useEffect(() => {
    let live = true;
    setTask(null); setError(null); setResult({ state: "idle" }); setConflict(null); setSolutionCode(null); setGate(null); setNextSlug(null);
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

  // ---- autosave: debounce, then one PUT at a time; the next Run awaits whatever is in flight
  const flush = useCallback(async () => {
    if (!dirtyRef.current || !etagRef.current) return;
    const sent = codeRef.current;
    try {
      const r = await api<{ etag: string }>(`/task/${encodeURIComponent(slug)}`, {
        method: "PUT", body: JSON.stringify({ code: sent, etag: etagRef.current }),
      });
      etagRef.current = r.etag;
      setSyntaxBad(false);
      if (codeRef.current === sent) { dirtyRef.current = false; setDirty(false); }
    } catch (e) {
      if (!(e instanceof ApiError)) throw e;
      if (e.status === 400) setSyntaxBad(true);                       // silent: an amber dot, no banner
      else if (e.status === 409 && e.detail?.etag) setConflict(e.detail);
      else if (e.status === 409) setGate({ at: "editor", message: e.detail?.error ?? e.message }); // no open attempt
      else setGate({ at: "editor", message: e.message });
    }
  }, [slug]);

  const edit = (next: string) => {
    setCode(next); codeRef.current = next;
    dirtyRef.current = true; setDirty(true);
    localStorage.setItem(draftKey(slug), JSON.stringify({ code: next, etag: etagRef.current }));
    clearTimeout(timer.current);
    timer.current = setTimeout(() => { inflight.current = flush(); }, AUTOSAVE_MS);
  };

  useEffect(() => () => { clearTimeout(timer.current); clearTimeout(gateTimer.current); }, [slug]);

  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => { if (dirtyRef.current) e.preventDefault(); };
    addEventListener("beforeunload", warn);
    return () => removeEventListener("beforeunload", warn);
  }, []);

  // ---- the clock: local ticks between heartbeats, server truth on every touch
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
      post<{ active: number }>(`/task/${encodeURIComponent(slug)}/touch`)
        .then((r) => setActive(r.active)).catch(() => {});
    }, HEARTBEAT_MS);
    return () => { clearInterval(tick); clearInterval(beat); };
  }, [hasAttempt, passed, slug]);

  // ---- actions
  const ensureOpen = async () => {
    if (hasAttempt) return;
    const p = await post<TaskData>(`/task/${encodeURIComponent(slug)}/open`);
    adopt(p, dirtyRef.current);            // never clobber text the learner already typed
  };

  const run = async () => {
    clearTimeout(timer.current);           // Run cancels the pending debounce…
    await inflight.current;                // …and rides the etag that PUT just returned
    setResult({ state: "running" });
    try {
      await ensureOpen();
      const r = await post<RunResult>(`/task/${encodeURIComponent(slug)}/run`, { code: codeRef.current, etag: etagRef.current });
      etagRef.current = r.etag;
      dirtyRef.current = false; setDirty(false); setSyntaxBad(false);
      if (r.passed) {
        localStorage.removeItem(draftKey(slug));
        setResult({ state: "passed", grade: r.grade!, box: r.box!, dueIn: r.due_in!, attempts: r.attempts, code: r.code! });
        setCode(r.code!);
        // what to do next lives on the catalogue, and only matters once the card is cleared
        api<Catalogue>("/catalogue")
          .then((c) => setNextSlug([...c.today.review, ...c.today.new].find((s) => s !== slug) ?? null))
          .catch(() => {});
      } else {
        setResult({ state: "failed", headline: r.headline.join("\n") || "The tests did not pass.", output: r.output });
        setTask((p) => p && p.attempt ? { ...p, attempt: { ...p.attempt, attempts: r.attempts } } : p);
      }
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 409 && err.detail?.etag) { setConflict(err.detail); setResult({ state: "idle" }); }
      else if (err.status === 400) { setSyntaxBad(true); setResult({ state: "failed", headline: `${err.detail?.error} (line ${err.detail?.line})`, output: "" }); }
      else { setResult({ state: "failed", headline: err.message, output: "" }); }
    }
  };

  const hint = async () => {
    try {
      await ensureOpen();
      const r = await post<{ level: number; total: number; text: string }>(`/task/${encodeURIComponent(slug)}/hint`);
      setGate(null);
      setTask((p) => p && ({ ...p, hints: { ...p.hints, shown: [...p.hints.shown, r.text] } }));
      setNextHintIn(null);
      api<TaskData>(`/task/${encodeURIComponent(slug)}`).then((p) => setNextHintIn(p.hints.next_in)).catch(() => {});
    } catch (e) {
      const err = e as ApiError;
      const wait = err.status === 423 ? err.detail?.wait_secs : 0;
      if (wait) {
        setNextHintIn(wait);
        flash(`Not yet — ${secs(wait)}. Keep working; hint ${(task?.hints.shown.length ?? 0) + 1} unlocks itself.`);
      } else setGate({ at: "hints", message: err.message });
    }
  };

  const solution = async () => {
    try {
      await ensureOpen();
      const r = await post<{ code: string }>(`/task/${encodeURIComponent(slug)}/solution`);
      setSolutionCode(r.code); setGate(null);
      setTask((p) => p && ({ ...p, solution: { ...p.solution, unlocked: true } }));
    } catch (e) {
      const err = e as ApiError;
      const d = err.detail ?? {};
      setGate({ at: "solution", message: d.need_attempts || d.need_secs
        ? `${err.message} — ${plural(d.need_attempts || 0, "more attempt")}, ${secs(d.need_secs || 0)} more work.`
        : err.message });
    }
  };

  const abandon = async () => {
    if (!confirm("Discard this attempt? The work is archived and the stub comes back.")) return;
    clearTimeout(timer.current);
    await inflight.current;
    try {
      const p = await post<TaskData>(`/task/${encodeURIComponent(slug)}/abandon`, { etag: etagRef.current });
      localStorage.removeItem(draftKey(slug));
      adopt(p); setResult({ state: "idle" }); setSolutionCode(null); setGate(null); setNextSlug(null);
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 409 && err.detail?.etag) setConflict(err.detail); else setGate({ at: "editor", message: err.message });
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

  const { meta, hints, solution: gateState, attempt } = task;
  const hintsLeft = hints.total - hints.shown.length;
  const hintReady = nextHintIn === null || nextHintIn <= 0;
  /** The gate banner, rendered only under the control that raised it. */
  const notice = (at: Exclude<Gate, null>["at"]) => gate?.at === at
    ? <div className="m-drop" style={{ marginTop: 10 }}><NoticeBanner message={gate.message} actions={[{ label: "Dismiss", onClick: () => setGate(null) }]} /></div>
    : null;

  // the run that produced this result, or the one being worked on now
  const attemptNo = passed ? result.attempts : attempt ? attempt.attempts + 1 : 0;

  return (
    <div style={{ maxWidth: 1500, margin: "0 auto" }}>
      {/* Meta bar: who the task is, how it is going, and where it sits in the tag tree. */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 14 }}>
        <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-faint)" }}>{meta.topic}</span>
        <h1 style={{ margin: 0, fontSize: "var(--fs-h)", fontWeight: 600 }}>{meta.title}</h1>
        <StatusBadge status={task.status} />
        <StatusBadge status={meta.difficulty} />
        <div style={{ flex: 1 }} />
        {/* D13: a tag reads as the path to it — `core/f-strings`. A track is its own chip. */}
        {meta.track ? <TagChip label={meta.track} small /> : null}
        {meta.tags.map((t) => <TagChip key={t} label={`${meta.tier}/${t}`} small />)}
        {meta.source ? <span style={ASIDE}>{meta.source}</span> : null}
      </div>

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        {/* native `resize` beats a drag handle: one declaration, real pointer affordance */}
        <div style={{ width: "42%", minWidth: 340, maxWidth: "70%", maxHeight: "calc(100vh - 148px)", overflow: "auto", resize: "horizontal" }}>
          <Card label={`Spec · ${slug}/README.md`}>
            <SpecText text={task.spec_md} slug={slug} hideTitle />

            <div style={{ marginTop: 22, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
              <div style={{ ...LABEL, marginBottom: 10 }}>
                Hints <span style={PLAIN}>· {hints.shown.length} of {hints.total} shown, unlocked by time on task</span>
              </div>
              {hints.shown.map((text, i) => (
                <div key={i} style={{ background: "var(--surface-2)", borderRadius: "var(--radius)", padding: "10px 12px", marginBottom: 8 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, letterSpacing: ".04em", textTransform: "uppercase", color: "var(--accent)", marginBottom: 4 }}>Hint {i + 1}</div>
                  <SpecText text={text} slug={slug} style={{ fontSize: 14 }} />
                </div>
              ))}
              {hintsLeft ? (
                <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
                  <Button variant="secondary" onClick={hint}>Show hint {hints.shown.length + 1}</Button>
                  <span style={ASIDE}>{hintReady ? "ready" : `unlocks in ${secs(nextHintIn!)}`}</span>
                </div>
              ) : (
                <div style={ASIDE}>All {hints.total} levels shown. Nothing else is gated except the solution.</div>
              )}
              {notice("hints")}
            </div>

            <div style={{ marginTop: 20, paddingTop: 16, borderTop: "1px solid var(--border)" }}>
              <div style={{ ...LABEL, marginBottom: 10 }}>
                Solution <span style={PLAIN}>· {solutionCode ? "revealed — this attempt is marked" : gateState.unlocked ? "unlocked" : `locked · needs ${plural(gateState.need_attempts, "more attempt")} and ${secs(gateState.need_secs)} more work`}</span>
              </div>
              {solutionCode ? (
                <div style={{ display: "grid", gap: 8 }}>
                  <NoticeBanner message="Solution shown — this pass won’t promote the card. It grades as struggled and stays in its box." actions={[]} />
                  <SpecText text={"```python\n" + solutionCode + "\n```"} slug={slug} />
                </div>
              ) : (
                <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
                  <Button variant="secondary" onClick={solution}>{gateState.unlocked ? "Show solution" : "Unlock solution"}</Button>
                  <span style={ASIDE}>taking it means this pass won’t promote</span>
                </div>
              )}
              {notice("solution")}
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
          {/* Anything the app noticed drops in above the work it is about. */}
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
          {gate?.at === "editor" ? <div className="m-drop"><NoticeBanner message={gate.message} actions={[{ label: "Dismiss", onClick: () => setGate(null) }]} /></div> : null}
          {task.has_given ? <NoticeBanner message="This task ships given code above solve() — read it, but leave it alone." actions={[]} /> : null}

          <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
            <Button kbdHint="Ctrl+Enter" onClick={run} disabled={result.state === "running" || passed}>
              {result.state === "running" ? "Running…" : "Run tests"}
            </Button>
            <Timer seconds={active} paused={!hasAttempt || passed} />
            <span className="tabular" style={{ fontSize: 13, color: "var(--text-muted)" }}>
              {attemptNo ? `attempt ${attemptNo}` : "not started"}
            </span>
            {attempt ? <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 12.5, color: "var(--text-faint)" }}>seed {attempt.seed}</span> : null}
            <div style={{ flex: 1 }} />
            {dirty || syntaxBad ? (
              <span style={{ fontSize: 12.5, color: syntaxBad ? "var(--warn)" : "var(--text-faint)" }}>
                ● {syntaxBad ? "not saved — syntax" : "unsaved"}
              </span>
            ) : null}
            {hasAttempt && !passed ? <Button variant="quiet" onClick={abandon} style={{ fontSize: 13 }}>Abandon</Button> : null}
          </div>

          <Editor value={code} onChange={edit} onRun={run} readOnly={passed} dark={dark} height="calc(100vh - 364px)" />

          {/* The result card re-enters on every state change — keyed so `.m-rise` replays. */}
          <div className="m-rise" key={result.state}>
            <Card label={attemptNo ? `Result · attempt ${attemptNo}` : "Result"} padding={16}>
              <ResultBanner
                state={result.state}
                headline={result.state === "failed" ? result.headline : undefined}
                gradeLine={passed ? `${result.grade.toUpperCase()} · ${secs(active)} · ${plural(result.attempts, "attempt")} · box ${result.box + 1} of 5` : undefined}
                backIn={passed ? plural(result.dueIn, "day") : undefined} />

              {result.state === "failed" && result.output ? (
                <Collapsible label="Full output" meta={`pytest · ${plural(result.output.trimEnd().split("\n").length, "line")}`} style={{ marginTop: 8 }}>
                  {result.output}
                </Collapsible>
              ) : null}

              {passed ? (
                <div style={{ marginTop: 10, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
                  <span className="m-step" style={{ display: "inline-flex" }}><LadderMeter box={result.box + 1} /></span>
                  <span style={{ fontSize: 13, color: "var(--text-muted)" }}>the card stepped up — code archived, stub restored for next time</span>
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
    </div>
  );
}
