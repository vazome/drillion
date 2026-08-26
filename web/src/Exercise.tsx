import { useCallback, useEffect, useRef, useState } from "react";
import { Button, Card, Collapsible, ConflictBanner, EmptyState, LadderMeter, NoticeBanner, ResultBanner, SpecText, StatusBadge, TagChip, Timer } from "./ds/index.js";
import { ApiError, api, post, type Exercise as Ex, type RunResult } from "./api";
import { Editor } from "./Editor";

const LABEL = { fontSize: "var(--fs-label)", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase" as const, color: "var(--text-muted)" };
const AUTOSAVE_MS = 800;
const HEARTBEAT_MS = 60_000;
const draftKey = (slug: string) => `drillion-draft-${slug}`;
const secs = (n: number) => n >= 60 ? `${Math.floor(n / 60)}m${String(n % 60).padStart(2, "0")}s` : `${n} s`;

type Result =
  | { state: "idle" | "running" }
  | { state: "failed"; headline: string; output: string }
  | { state: "passed"; grade: string; box: number; dueIn: number; attempts: number; code: string };

export function Exercise({ slug, dark }: { slug: string; dark: boolean }) {
  const [ex, setEx] = useState<Ex | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [dirty, setDirty] = useState(false);
  const [syntaxBad, setSyntaxBad] = useState(false);
  const [result, setResult] = useState<Result>({ state: "idle" });
  const [conflict, setConflict] = useState<{ etag: string; code: string } | null>(null);
  const [draftOffer, setDraftOffer] = useState<string | null>(null);
  const [gate, setGate] = useState<string | null>(null);
  const [solutionCode, setSolutionCode] = useState<string | null>(null);
  const [active, setActive] = useState(0);
  const [nextHintIn, setNextHintIn] = useState<number | null>(null);

  // Refs carry the live values into the async chain; state alone would capture a stale closure.
  const codeRef = useRef(""), etagRef = useRef(""), dirtyRef = useRef(false);
  const timer = useRef<number | undefined>(undefined);
  const inflight = useRef<Promise<void> | null>(null);
  const hasAttempt = !!ex?.attempt;
  const passed = result.state === "passed";

  const adopt = useCallback((p: Ex, keepCode = false) => {
    setEx(p); etagRef.current = p.etag;
    setActive(p.attempt?.active ?? 0);
    setNextHintIn(p.hints.next_in);
    if (!keepCode) { setCode(p.code); codeRef.current = p.code; setDirty(false); dirtyRef.current = false; }
  }, []);

  // ---- load, and offer a newer local draft over what the file holds
  useEffect(() => {
    let live = true;
    setEx(null); setError(null); setResult({ state: "idle" }); setConflict(null); setSolutionCode(null); setGate(null);
    api<Ex>(`/ex/${encodeURIComponent(slug)}`).then((p) => {
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
      const r = await api<{ etag: string }>(`/ex/${encodeURIComponent(slug)}`, {
        method: "PUT", body: JSON.stringify({ code: sent, etag: etagRef.current }),
      });
      etagRef.current = r.etag;
      setSyntaxBad(false);
      if (codeRef.current === sent) { dirtyRef.current = false; setDirty(false); }
    } catch (e) {
      if (!(e instanceof ApiError)) throw e;
      if (e.status === 400) setSyntaxBad(true);                       // silent: an amber dot, no banner
      else if (e.status === 409 && e.detail?.etag) setConflict(e.detail);
      else if (e.status === 409) setGate(e.detail?.error ?? e.message); // no open attempt
      else setGate(e.message);
    }
  }, [slug]);

  const edit = (next: string) => {
    setCode(next); codeRef.current = next;
    dirtyRef.current = true; setDirty(true);
    localStorage.setItem(draftKey(slug), JSON.stringify({ code: next, etag: etagRef.current }));
    clearTimeout(timer.current);
    timer.current = setTimeout(() => { inflight.current = flush(); }, AUTOSAVE_MS);
  };

  useEffect(() => () => clearTimeout(timer.current), [slug]);

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
      post<{ active: number }>(`/ex/${encodeURIComponent(slug)}/touch`)
        .then((r) => setActive(r.active)).catch(() => {});
    }, HEARTBEAT_MS);
    return () => { clearInterval(tick); clearInterval(beat); };
  }, [hasAttempt, passed, slug]);

  // ---- actions
  const ensureOpen = async () => {
    if (hasAttempt) return;
    const p = await post<Ex>(`/ex/${encodeURIComponent(slug)}/open`);
    adopt(p, dirtyRef.current);            // never clobber text the learner already typed
  };

  const run = async () => {
    clearTimeout(timer.current);           // Run cancels the pending debounce…
    await inflight.current;                // …and rides the etag that PUT just returned
    setResult({ state: "running" });
    try {
      await ensureOpen();
      const r = await post<RunResult>(`/ex/${encodeURIComponent(slug)}/run`, { code: codeRef.current, etag: etagRef.current });
      etagRef.current = r.etag;
      dirtyRef.current = false; setDirty(false); setSyntaxBad(false);
      if (r.passed) {
        localStorage.removeItem(draftKey(slug));
        setResult({ state: "passed", grade: r.grade!, box: r.box!, dueIn: r.due_in!, attempts: r.attempts, code: r.code! });
        setCode(r.code!);
      } else {
        setResult({ state: "failed", headline: r.headline.join("\n") || "The tests did not pass.", output: r.output });
        setEx((p) => p && p.attempt ? { ...p, attempt: { ...p.attempt, attempts: r.attempts } } : p);
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
      const r = await post<{ level: number; total: number; text: string }>(`/ex/${encodeURIComponent(slug)}/hint`);
      setGate(null);
      setEx((p) => p && ({ ...p, hints: { ...p.hints, shown: [...p.hints.shown, r.text] } }));
      setNextHintIn(null);
      api<Ex>(`/ex/${encodeURIComponent(slug)}`).then((p) => setNextHintIn(p.hints.next_in)).catch(() => {});
    } catch (e) {
      const err = e as ApiError;
      setGate(err.message);
      if (err.status === 423 && err.detail?.wait_secs) setNextHintIn(err.detail.wait_secs);
    }
  };

  const solution = async () => {
    try {
      await ensureOpen();
      const r = await post<{ code: string }>(`/ex/${encodeURIComponent(slug)}/solution`);
      setSolutionCode(r.code); setGate(null);
      setEx((p) => p && ({ ...p, solution: { ...p.solution, unlocked: true } }));
    } catch (e) {
      const err = e as ApiError;
      const d = err.detail ?? {};
      setGate(d.need_attempts || d.need_secs
        ? `${err.message} — ${d.need_attempts || 0} more attempt(s), ${secs(d.need_secs || 0)} more work.`
        : err.message);
    }
  };

  const abandon = async () => {
    if (!confirm("Discard this attempt? The work is archived and the stub comes back.")) return;
    clearTimeout(timer.current);
    await inflight.current;
    try {
      const p = await post<Ex>(`/ex/${encodeURIComponent(slug)}/abandon`, { etag: etagRef.current });
      localStorage.removeItem(draftKey(slug));
      adopt(p); setResult({ state: "idle" }); setSolutionCode(null); setGate(null);
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 409 && err.detail?.etag) setConflict(err.detail); else setGate(err.message);
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
  if (!ex) return <EmptyState message="Loading…" />;

  const { meta, hints, solution: gateState, attempt } = ex;
  const hintsLeft = hints.total - hints.shown.length;
  const hintReady = nextHintIn === null || nextHintIn <= 0;

  return (
    <div style={{ display: "flex", gap: 20, alignItems: "flex-start", maxWidth: 1500, margin: "0 auto" }}>
      {/* native `resize` beats a drag handle: one declaration, real pointer affordance */}
      <div style={{ width: "42%", minWidth: 340, maxWidth: "70%", maxHeight: "calc(100vh - 104px)", overflow: "auto", resize: "horizontal" }}>
        <Card label={`${meta.topic} · ${meta.title}`}>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", marginBottom: 14 }}>
            <StatusBadge status={ex.status} />
            {meta.tags.map((t) => <TagChip key={t} label={t} small />)}
            <span className="tabular" style={{ fontFamily: "var(--font-mono)", fontSize: 12.5, color: "var(--text-muted)" }}>{meta.minutes} min par</span>
            {meta.source ? <span style={{ fontSize: 12.5, color: "var(--text-faint)" }}>{meta.source}</span> : null}
          </div>
          <SpecText text={ex.spec_md} slug={slug} />

          <div style={{ ...LABEL, margin: "22px 0 8px" }}>
            Hints <span style={{ fontWeight: 400, textTransform: "none", letterSpacing: 0 }}>· {hints.total} levels, unlocked by time on task</span>
          </div>
          {hints.shown.map((text, i) => (
            <div key={i} style={{ background: "var(--surface-2)", borderRadius: "var(--radius)", padding: "10px 12px", marginBottom: 8 }}>
              <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 2 }}>Hint {i + 1}</div>
              <SpecText text={text} slug={slug} style={{ fontSize: 14 }} />
            </div>
          ))}
          <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
            <Button variant="quiet" onClick={hint} disabled={hintsLeft === 0 || !hintReady}>
              {hintsLeft === 0 ? "No hints left" : hintReady ? `Show hint ${hints.shown.length + 1}` : `Hint ${hints.shown.length + 1} in ${secs(nextHintIn!)}`}
            </Button>
            <Button variant="quiet" onClick={solution} disabled={!!solutionCode}>
              {gateState.unlocked || solutionCode ? "Show solution" : "Solution — locked"}
            </Button>
          </div>
          {!gateState.unlocked && !solutionCode ? (
            <div style={{ fontSize: 13, color: "var(--text-faint)", marginTop: 8 }}>
              Needs {gateState.need_attempts} more attempt(s) and {secs(gateState.need_secs)} more work; taking it means this pass won’t promote.
            </div>
          ) : null}
          {solutionCode ? (
            <Collapsible label="Solution" defaultOpen style={{ marginTop: 10 }}><code>{solutionCode}</code></Collapsible>
          ) : null}
          {ex.archive.length ? (
            <Collapsible label={`Archive · ${ex.archive.length} previous pass(es)`} mono={false} style={{ marginTop: 12 }}>
              {ex.archive.slice().reverse().map((a, i) => (
                <div key={i} style={{ marginBottom: 8 }}>
                  <div style={{ display: "flex", gap: 10, alignItems: "center", fontSize: 13 }}>
                    <span className="tabular" style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>{a.date}</span>
                    <StatusBadge status={a.grade.toLowerCase()} />
                  </div>
                  {a.code ? <pre style={{ margin: "6px 0 0", fontSize: 12.5, whiteSpace: "pre-wrap", color: "var(--text-muted)" }}>{a.code}</pre> : null}
                </div>
              ))}
            </Collapsible>
          ) : null}
        </Card>
      </div>

      <div style={{ flex: 1, minWidth: 420, display: "grid", gap: 12 }}>
        {conflict ? <ConflictBanner detail="Your draft and the file on disk have diverged." onReload={takeDisk} onKeep={keepMine} /> : null}
        {draftOffer ? (
          <NoticeBanner message="A newer local draft exists for this drill."
            actions={[
              { label: "Restore it", onClick: () => { edit(draftOffer); setDraftOffer(null); } },
              { label: "Discard", onClick: () => { localStorage.removeItem(draftKey(slug)); setDraftOffer(null); } },
            ]} />
        ) : null}
        {gate ? <NoticeBanner message={gate} actions={[{ label: "Dismiss", onClick: () => setGate(null) }]} /> : null}
        {ex.has_given ? <NoticeBanner message="This drill ships given code above solve() — read it, but leave it alone." actions={[]} /> : null}

        <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
          <Button kbdHint="Ctrl+Enter" onClick={run} disabled={result.state === "running" || passed}>
            {result.state === "running" ? "Running…" : "Run tests"}
          </Button>
          <Timer seconds={active} parMinutes={meta.minutes} paused={!hasAttempt} />
          <span className="tabular" style={{ fontSize: 13, color: "var(--text-muted)" }}>
            {attempt ? `attempt ${attempt.attempts + (passed ? 0 : 1)}` : "not started"}
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

        <Editor value={code} onChange={edit} onRun={run} readOnly={passed} dark={dark} height="calc(100vh - 320px)" />

        <ResultBanner
          state={result.state}
          headline={result.state === "failed" ? result.headline : undefined}
          output={result.state === "failed" ? result.output : undefined}
          gradeLine={passed ? `${result.grade} · ${secs(active)} · ${result.attempts} attempt(s) · box ${result.box + 1} of 5` : undefined}
          backIn={passed ? `${result.dueIn} days` : undefined} />

        {passed ? (
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <LadderMeter box={result.box + 1} />
            <span style={{ fontSize: 13, color: "var(--text-muted)" }}>the card stepped up — code archived, stub restored for next time</span>
            <div style={{ flex: 1 }} />
            <Button onClick={() => { location.hash = "#/"; }}>Back to Today</Button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
