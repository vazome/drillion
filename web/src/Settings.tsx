import { useEffect, useRef, useState, type ReactNode } from "react";
import { Button, Card, EmptyState, Input, NoticeBanner, Select, Toggle } from "./ds/index.js";
import { api, type Paths, type Bundle, type Erased, type Restored } from "./api";
import { DEFAULTS, FONTS, setPrefs, usePrefs } from "./prefs";

/** A path plus the one thing anyone wants to do with it. */
function Location({ label, path }: { label: string; path: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard?.writeText(path).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }, () => {});
  };
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: 12, padding: "6px 0" }}>
      <span style={{ fontSize: 13, color: "var(--text-muted)", minWidth: 110 }}>{label}</span>
      <code style={{ flex: 1, fontSize: 13, overflowWrap: "anywhere" }}>{path}</code>
      <Button variant="quiet" onClick={copy}>{copied ? "Copied" : "Copy"}</Button>
    </div>
  );
}

/** Typed exactly, or the button stays off. The server checks the same phrase, because this
 *  route is reachable without the screen in front of it. */
const PHRASE = "erase progress";

/** The one screen area that destroys data, drawn so it cannot be mistaken for the rest of
 *  Settings: red frame, red heading, and a confirmation that has to be typed rather than
 *  clicked through. */
function DangerZone() {
  const [open, setOpen] = useState(false);
  const [typed, setTyped] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<Erased | null>(null);

  const close = () => { setOpen(false); setTyped(""); setError(null); };
  const erase = async () => {
    setBusy(true);
    try {
      setDone(await api<Erased>("/reset", { method: "POST", body: JSON.stringify({ confirm: typed }) }));
      close();
    } catch (e) { setError((e as Error).message); }
    setBusy(false);
  };

  return (
    <Card label="Danger zone" style={{ border: "1px solid var(--fail)", boxShadow: "none" }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
        <div style={{ flex: 1, minWidth: 280 }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: "var(--fail)" }}>Erase all progress</div>
          <p style={{ margin: "4px 0 0", fontSize: 14, color: "var(--text-muted)" }}>
            Deletes the progress database itself, so your schedule, your history and your
            notes are gone rather than emptied, and puts every task back to a{" "}
            <code>solve()</code> that raises, the way Abandon does for one. A backup of
            everything is written first, so a restore can undo it. Nothing else can.
          </p>
        </div>
        {open ? null : (
          <Button variant="secondary" style={{ color: "var(--fail)", borderColor: "var(--fail)" }} onClick={() => setOpen(true)}>
            Erase all progress
          </Button>
        )}
      </div>

      {open ? (
        <div style={{ marginTop: 14, padding: 14, borderRadius: "var(--radius)", background: "var(--fail-bg)", display: "grid", gap: 10 }}>
          <div style={{ fontSize: 14 }}>
            To confirm, type <code style={{ fontWeight: 600 }}>{PHRASE}</code> below.
          </div>
          <Input
            value={typed} onChange={setTyped} mono placeholder={PHRASE}
            ariaLabel={`Type ${PHRASE} to confirm`} style={{ maxWidth: 280 }}
          />
          {error ? <NoticeBanner message={error} /> : null}
          <div style={{ display: "flex", gap: 10 }}>
            <Button
              variant="secondary" disabled={busy || typed.trim() !== PHRASE} onClick={erase}
              style={typed.trim() === PHRASE && !busy ? { background: "var(--fail)", borderColor: "var(--fail)", color: "#FFFFFF" } : undefined}>
              {busy ? "Erasing…" : "I understand, erase everything"}
            </Button>
            <Button variant="quiet" disabled={busy} onClick={close}>Cancel</Button>
          </div>
        </div>
      ) : null}

      {done ? (
        <div style={{ marginTop: 14, display: "grid", gap: 8 }}>
          <div style={{ fontSize: 14 }}>Erased. {done.cleared} task files went back to their stub.</div>
          {done.failed.length ? <NoticeBanner message={`The code could not be cleared for: ${done.failed.join(", ")}`} /> : null}
          <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
            What you had is at <code>{done.kept}</code>.
          </div>
          <div><Button onClick={() => { location.hash = "#/"; location.reload(); }}>Back to the catalogue</Button></div>
        </div>
      ) : null}
    </Card>
  );
}

/** One preference: what it is called, the control, and a line saying what it buys you. */
function Row({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "7px 0", flexWrap: "wrap" }}>
      <span style={{ fontSize: 14, minWidth: 150 }}>{label}</span>
      {children}
      {hint ? <span style={{ fontSize: 13, color: "var(--text-faint)", flex: 1, minWidth: 180 }}>{hint}</span> : null}
    </div>
  );
}

const SIZES = ["12", "13", "14", "16", "18"];
const TABS = ["2", "4", "8"];

/** How the editor is set, and whether the clock is on screen. Every row is a preference of
 *  this browser: none of it is in your progress, and none of it travels in a backup. */
function EditorSettings() {
  const prefs = usePrefs();
  const untouched = JSON.stringify(prefs) === JSON.stringify(DEFAULTS);
  return (
    <Card label="Editor">
      <Row label="Font">
        <Select value={prefs.font} ariaLabel="Editor font" style={{ minWidth: 190 }}
          options={FONTS.map((f) => ({ value: f.value, label: f.label }))}
          onChange={(v) => setPrefs({ font: v as typeof prefs.font })} />
      </Row>
      <Row label="Font size">
        <Select value={String(prefs.fontSize)} options={SIZES} ariaLabel="Editor font size"
          onChange={(v) => setPrefs({ fontSize: Number(v) })} style={{ minWidth: 90 }} />
      </Row>
      <Row label="Font ligatures" hint="Draws ==, != and -> as one glyph.">
        <Toggle checked={prefs.ligatures} label={prefs.ligatures ? "On" : "Off"}
          onChange={(on) => setPrefs({ ligatures: on })} />
      </Row>
      <Row label="Key binding" hint="Ctrl+Enter runs and Ctrl+Shift+Enter submits whichever you pick, and C-g always gets you out of a half-typed Emacs chord.">
        <Select value={prefs.keys} ariaLabel="Key binding" style={{ minWidth: 140 }}
          options={[{ value: "regular", label: "Standard" }, { value: "vim", label: "Vim" }, { value: "emacs", label: "Emacs" }]}
          onChange={(v) => setPrefs({ keys: v as typeof prefs.keys })} />
      </Row>
      <Row label="Tab size">
        <Select value={String(prefs.tabSize)} options={TABS} ariaLabel="Tab size"
          onChange={(v) => setPrefs({ tabSize: Number(v) })} style={{ minWidth: 90 }} />
      </Row>
      <Row label="Word wrap" hint="Off puts long lines behind a horizontal scrollbar.">
        <Toggle checked={prefs.wordWrap} label={prefs.wordWrap ? "On" : "Off"}
          onChange={(on) => setPrefs({ wordWrap: on })} />
      </Row>
      <Row label="Relative line numbers" hint="Counts from the cursor, the way Vim motions do.">
        <Toggle checked={prefs.relativeLines} label={prefs.relativeLines ? "On" : "Off"}
          onChange={(on) => setPrefs({ relativeLines: on })} />
      </Row>
      <Row label="Practice timer" hint="Hiding it changes nothing about the time: it is still counted, and it still grades.">
        <Toggle checked={prefs.showTimer} label={prefs.showTimer ? "Shown" : "Hidden"}
          onChange={(on) => setPrefs({ showTimer: on })} />
      </Row>
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginTop: 6 }}>
        {untouched ? null : (
          <Button variant="quiet" onClick={() => setPrefs(DEFAULTS)}>Put these back to their defaults</Button>
        )}
        <span style={{ fontSize: 13, color: "var(--text-faint)" }}>
          These live in this browser, so they are not part of a backup.
        </span>
      </div>
    </Card>
  );
}

const counts = (b: Bundle["brings"]) =>
  `${b.cards} cards, ${b.archive} solved tasks, ${b.notes} notes, ${b.tasks} saved task files`;

export function Settings() {
  const [paths, setPaths] = useState<Paths | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<Bundle | null>(null);
  const [done, setDone] = useState<Restored | null>(null);
  const [busy, setBusy] = useState(false);
  const picker = useRef<HTMLInputElement>(null);

  useEffect(() => { api<Paths>("/settings").then(setPaths).catch((e) => setError(e.message)); }, []);

  /** Reading the bundle is its own step: nothing is replaced until the summary is accepted. */
  const choose = async (chosen: File | null) => {
    setFile(chosen); setPreview(null); setDone(null); setError(null);
    if (!chosen) return;
    setBusy(true);
    try {
      setPreview(await api<Bundle>("/restore/preview", {
        method: "POST", body: await chosen.arrayBuffer(), headers: { "content-type": "application/zip" },
      }));
    } catch (e) { setError((e as Error).message); }
    setBusy(false);
  };

  const apply = async () => {
    if (!file) return;
    setBusy(true);
    try {
      setDone(await api<Restored>("/restore", {
        method: "POST", body: await file.arrayBuffer(), headers: { "content-type": "application/zip" },
      }));
      setPreview(null); setFile(null);
      if (picker.current) picker.current.value = "";
    } catch (e) { setError((e as Error).message); }
    setBusy(false);
  };

  if (error && !paths) return <EmptyState message={`Could not load settings: ${error}`} />;

  return (
    <div style={{ display: "grid", gap: 18 }}>
      <Card label="Your data">
        <p style={{ margin: "0 0 8px", fontSize: 14, color: "var(--text-muted)" }}>
          Everything drillion knows about your practice lives on this machine, in these places.
        </p>
        {paths ? (
          <>
            <Location label="Data folder" path={paths.root} />
            <Location label="Progress" path={paths.progress} />
            <Location label="Tasks" path={paths.tasks} />
          </>
        ) : <EmptyState message="Loading…" align="left" />}
      </Card>

      <EditorSettings />

      <Card label="Back up">
        <p style={{ margin: "0 0 12px", fontSize: 14, color: "var(--text-muted)" }}>
          One file holding your schedule, your history and the code you have written. Keep it
          anywhere. Restoring it on another machine, or after a reinstall, picks up where you left off.
        </p>
        <a href="/api/backup" download style={{ textDecoration: "none" }}>
          <Button variant="primary">Download a backup</Button>
        </a>
      </Card>

      <Card label="Restore">
        <p style={{ margin: "0 0 12px", fontSize: 14, color: "var(--text-muted)" }}>
          Restoring replaces your current progress and the code saved in every task. It
          happens completely or not at all, and what it replaces is written to a backup of
          its own first, so you can undo it.
        </p>
        <input
          ref={picker} type="file" accept=".zip,application/zip" disabled={busy}
          aria-label="Choose a backup file to restore"
          onChange={(e) => choose(e.target.files?.[0] ?? null)}
          style={{ fontSize: 14, color: "var(--text-muted)" }}
        />
        {error && paths ? <NoticeBanner message={error} style={{ marginTop: 12 }} /> : null}
        {preview ? (
          <div style={{ marginTop: 14, display: "grid", gap: 8 }}>
            <div style={{ fontSize: 14 }}>
              Taken {preview.created?.replace("T", " at ") ?? "at an unknown time"} on drillion v{preview.drillion}.
            </div>
            <div style={{ fontSize: 14 }}>Brings back {counts(preview.brings)}.</div>
            <div style={{ fontSize: 14, color: "var(--text-muted)" }}>
              Replaces {preview.replaces.cards} cards, {preview.replaces.archive} solved tasks
              and {preview.replaces.notes} notes you have now.
            </div>
            {preview.unknown.length ? (
              <NoticeBanner message={`${preview.unknown.length} task${preview.unknown.length > 1 ? "s" : ""} in this backup are not in this version of drillion, so their saved code stays in the file: ${preview.unknown.join(", ")}`} />
            ) : null}
            <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
              <Button variant="primary" disabled={busy} onClick={apply}>Replace my data</Button>
              <Button variant="quiet" disabled={busy} onClick={() => choose(null)}>Cancel</Button>
            </div>
          </div>
        ) : null}
        {done ? (
          <div style={{ marginTop: 14, display: "grid", gap: 8 }}>
            <div style={{ fontSize: 14 }}>Restored {counts(done.brings)}.</div>
            <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
              What you had before is at <code>{done.kept}</code>.
            </div>
            <div><Button onClick={() => { location.hash = "#/"; location.reload(); }}>Back to the catalogue</Button></div>
          </div>
        ) : null}
      </Card>

      <DangerZone />
    </div>
  );
}
