import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { Button, EmptyState, Input, NoticeBanner, Select, Toggle } from "./ds/index.js";
import { api, type Paths, type Bundle, type Erased, type Restored } from "./api";
import { DEFAULTS, FONTS, setPrefs, usePrefs } from "./prefs";
import s from "./Settings.module.css";

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
    <Row label={label}>
      <code className={s.path}>{path}</code>
      <Button variant="quiet" onClick={copy}>{copied ? "Copied" : "Copy"}</Button>
    </Row>
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
    <div className={s.dangerZone}>
      <div className={s.dangerHead}>
        <div className={s.dangerText}>
          <div className={s.dangerTitle}>Erase all progress</div>
          <p className={s.dangerDescription}>
            Deletes the progress database itself, so your schedule, your history and your
            notes are gone rather than emptied, and puts every task back to a{" "}
            <code>solve()</code> that raises, the way Abandon does for one. A backup of
            everything is written first, so a restore can undo it. Nothing else can.
          </p>
        </div>
        {open ? null : (
          <Button variant="secondary" className={s.dangerButton} onClick={() => setOpen(true)}>
            Erase all progress
          </Button>
        )}
      </div>

      {open ? (
        <div className={s.confirmation}>
          <div>
            To confirm, type <code className={s.phrase}>{PHRASE}</code> below.
          </div>
          <Input
            value={typed} onChange={setTyped} mono placeholder={PHRASE}
            ariaLabel={`Type ${PHRASE} to confirm`} className={s.confirmInput}
          />
          {error ? <NoticeBanner message={error} /> : null}
          <div className={s.actions}>
            <Button
              variant="secondary" disabled={busy || typed.trim() !== PHRASE} onClick={erase}
              className={s.confirmButton}>
              {busy ? "Erasing…" : "I understand, erase everything"}
            </Button>
            <Button variant="quiet" disabled={busy} onClick={close}>Cancel</Button>
          </div>
        </div>
      ) : null}

      {done ? (
        <div className={s.result}>
          <div>Erased. {done.cleared} task files went back to their stub.</div>
          {done.failed.length ? <NoticeBanner message={`The code could not be cleared for: ${done.failed.join(", ")}`} /> : null}
          <div className={s.kept}>
            What you had is at <code>{done.kept}</code>.
          </div>
          <div><Button onClick={() => { location.hash = "#/"; location.reload(); }}>Back to the catalogue</Button></div>
        </div>
      ) : null}
    </div>
  );
}

/** One preference: what it is called, the control, and a line saying what it buys you. */
function Row({ label, hint, children }: { label: string; hint?: ReactNode; children: ReactNode }) {
  const id = useId();
  return (
    <div className={s.row} role="group" aria-labelledby={id}>
      <div className={s.rowLabel}>
        <div id={id}>{label}</div>
        {hint ? <div className={s.hint}>{hint}</div> : null}
      </div>
      <div className={s.control}>{children}</div>
    </div>
  );
}

/** Headings share the sheet's one scroll area; sections do not add another card or scroller. */
function Section({ title, note, children }: {
  title: string; note?: string; children: ReactNode;
}) {
  const id = useId();
  return (
    <section aria-labelledby={id}>
      <h3 id={id} className={s.sectionTitle}>{title}</h3>
      {note ? <p className={s.sectionNote}>{note}</p> : null}
      <div className={s.sectionBody}>{children}</div>
    </section>
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
    <Section title="Editor" note="These live in this browser, so they are not part of a backup.">
      <div>
      <Row label="Font">
        <Select value={prefs.font} ariaLabel="Editor font" className={s.fontSelect}
          options={FONTS.map((f) => ({ value: f.value, label: f.label }))}
          onChange={(v) => setPrefs({ font: v as typeof prefs.font })} />
      </Row>
      <Row label="Font size">
        <Select value={String(prefs.fontSize)} options={SIZES} ariaLabel="Editor font size"
          onChange={(v) => setPrefs({ fontSize: Number(v) })} className={s.numberSelect} />
      </Row>
      <Row label="Font ligatures" hint="== and -> as one glyph.">
        <Toggle checked={prefs.ligatures} label={prefs.ligatures ? "On" : "Off"}
          onChange={(on) => setPrefs({ ligatures: on })} />
      </Row>
      <Row label="Key binding" hint={<span>Ctrl+Enter runs and Ctrl+Shift+Enter submits whichever you pick, and <code>C-g</code> always gets you out of a half-typed Emacs chord.</span>}>
        <Select value={prefs.keys} ariaLabel="Key binding" className={s.keySelect}
          options={[{ value: "regular", label: "Standard" }, { value: "vim", label: "Vim" }, { value: "emacs", label: "Emacs" }]}
          onChange={(keys) => setPrefs({ keys: keys as typeof prefs.keys })} />
      </Row>
      <Row label="Tab size">
        <Select value={String(prefs.tabSize)} options={TABS} ariaLabel="Tab size"
          onChange={(v) => setPrefs({ tabSize: Number(v) })} className={s.numberSelect} />
      </Row>
      <Row label="Word wrap" hint="Off puts long lines behind a horizontal scrollbar.">
        <Toggle checked={prefs.wordWrap} label={prefs.wordWrap ? "On" : "Off"}
          onChange={(on) => setPrefs({ wordWrap: on })} />
      </Row>
      <Row label="Relative line numbers" hint="Counts from the cursor.">
        <Toggle checked={prefs.relativeLines} label={prefs.relativeLines ? "On" : "Off"}
          onChange={(on) => setPrefs({ relativeLines: on })} />
      </Row>
      <Row label="Practice timer" hint="Hiding it changes nothing about the time: it is still counted, and it still grades.">
        <Toggle checked={prefs.showTimer} label={prefs.showTimer ? "Shown" : "Hidden"}
          onChange={(on) => setPrefs({ showTimer: on })} />
      </Row>
      </div>
      {untouched ? null : (
        <div className={s.defaults}>
          <Button variant="quiet" onClick={() => setPrefs(DEFAULTS)}>Put these back to their defaults</Button>
        </div>
      )}
    </Section>
  );
}

const counts = (b: Bundle["brings"]) =>
  `${b.cards} cards, ${b.archive} solved tasks, ${b.notes} notes, ${b.tasks} saved task files`;

export function Settings() {
  const [paths, setPaths] = useState<Paths | null>(null);
  const [pathError, setPathError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<Bundle | null>(null);
  const [done, setDone] = useState<Restored | null>(null);
  const [busy, setBusy] = useState(false);
  const picker = useRef<HTMLInputElement>(null);

  useEffect(() => { api<Paths>("/settings").then(setPaths).catch((e) => setPathError(e.message)); }, []);

  /** Reading the bundle is its own step: nothing is replaced until the summary is accepted. */
  const choose = async (chosen: File | null) => {
    setFile(chosen); setPreview(null); setDone(null); setError(null);
    if (!chosen) {
      if (picker.current) picker.current.value = "";
      return;
    }
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

  return (
    <div className={s.sheet}>
      <EditorSettings />

      <Section title="Your data" note="Everything drillion knows about your practice lives on this machine, in these places.">
        {pathError ? <EmptyState message={`Could not load settings: ${pathError}`} /> : paths ? (
          <>
            <Location label="Data folder" path={paths.root} />
            <Location label="Progress" path={paths.progress} />
            <Location label="Tasks" path={paths.tasks} />
          </>
        ) : <EmptyState message="Loading…" align="left" />}
      </Section>

      <Section title="Back up" note="One file holding your schedule, your history and the code you have written. Keep it anywhere. Restoring it on another machine, or after a reinstall, picks up where you left off.">
        <a href="/api/backup" download data-variant="primary" className={s.download}>Download a backup</a>
      </Section>

      <Section title="Restore" note="Restoring replaces your current progress and the code saved in every task. It happens completely or not at all, and what it replaces is written to a backup of its own first, so you can undo it.">
        <input
          ref={picker} type="file" accept=".zip,application/zip" disabled={busy}
          aria-label="Choose a backup file to restore"
          onChange={(e) => choose(e.target.files?.[0] ?? null)}
          className={s.picker}
        />
        {error ? <NoticeBanner message={error} className={s.error} /> : null}
        {preview ? (
          <div className={s.result}>
            <div>
              Taken {preview.created?.replace("T", " at ") ?? "at an unknown time"} on drillion v{preview.drillion}.
            </div>
            <div>Brings back {counts(preview.brings)}.</div>
            <div className={s.muted}>
              Replaces {preview.replaces.cards} cards, {preview.replaces.archive} solved tasks
              and {preview.replaces.notes} notes you have now.
            </div>
            {preview.unknown.length ? (
              <NoticeBanner message={`${preview.unknown.length} task${preview.unknown.length > 1 ? "s" : ""} in this backup are not in this version of drillion, so their saved code stays in the file: ${preview.unknown.join(", ")}`} />
            ) : null}
            <div className={s.restoreActions}>
              <Button variant="primary" disabled={busy} onClick={apply}>Replace my data</Button>
              <Button variant="quiet" disabled={busy} onClick={() => choose(null)}>Cancel</Button>
            </div>
          </div>
        ) : null}
        {done ? (
          <div className={s.result}>
            <div>Restored {counts(done.brings)}.</div>
            <div className={s.kept}>
              What you had before is at <code>{done.kept}</code>.
            </div>
            <div><Button onClick={() => { location.hash = "#/"; location.reload(); }}>Back to the catalogue</Button></div>
          </div>
        ) : null}
      </Section>

      <Section title="Danger zone"><DangerZone /></Section>
    </div>
  );
}
