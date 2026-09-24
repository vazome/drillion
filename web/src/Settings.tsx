import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { Button, EmptyState, Icon, Input, NoticeBanner, Select, Toggle } from "./ds/index.js";
import { api, type Paths, type Bundle, type Erased, type Restored } from "./api";
import { DEFAULTS, FONTS, setPrefs, usePrefs } from "./prefs";
import type { IconName } from "./ds/index.js";
import s from "./Settings.module.css";

/** A path plus the one thing anyone wants to do with it. */
function Location({ label, icon, path }: { label: string; icon: IconName; path: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard?.writeText(path).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }, () => {});
  };
  return (
    <div className={s.place}>
      <Icon name={icon} />
      <span className={s.placeLabel}>{label}</span>
      <code className={s.path}>{path}</code>
      <button type="button" onClick={copy} className={s.small} aria-label={`Copy the ${label.toLowerCase()} path`}><Icon name="Copy" size={14} />{copied ? "Copied" : "Copy"}</button>
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
  const [typed, setTyped] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<Erased | null>(null);
  const id = useId();

  const erase = async () => {
    setBusy(true);
    try {
      setDone(await api<Erased>("/reset", { method: "POST", body: JSON.stringify({ confirm: typed }) }));
      setTyped(""); setError(null);
    } catch (e) { setError((e as Error).message); }
    setBusy(false);
  };

  return (
    <section aria-labelledby={id} className={s.danger}>
      <h3 id={id} className={s.title}>Danger zone</h3>
      <p className={s.text}>
        Erases your progress and puts every task back to its stub. A backup is written first; it is
        the only way back, and you will be told where it is.
      </p>
      {done ? (
        <div className={s.result}>
          <div>Erased. {done.cleared} task files went back to their stub.</div>
          {done.failed.length ? <NoticeBanner message={`The code could not be cleared for: ${done.failed.join(", ")}`} /> : null}
          <div className={s.kept}><Icon name="Archive" />What you had is at <code>{done.kept}</code>.</div>
          <div><Button onClick={() => { location.hash = "#/"; location.reload(); }}><Icon name="ArrowLeft" />Back to the catalogue</Button></div>
        </div>
      ) : <>
        <p className={s.text}>Type <code className={s.phrase}>{PHRASE}</code> to confirm</p>
        <div className={s.confirm}>
          <Input value={typed} onChange={setTyped} mono ariaLabel={`Type ${PHRASE} to confirm`} className={s.confirmInput} />
          <button type="button" disabled={busy || typed.trim() !== PHRASE} onClick={erase} className={s.erase}>
            <Icon name="TrashCan" size={14} />{busy ? "Erasing…" : "Erase all progress"}
          </button>
        </div>
        {error ? <NoticeBanner message={error} /> : null}
      </>}
    </section>
  );
}

/** One of a few choices, all in view: the key binding, the tab size, whether the clock shows. */
function Choice<T extends string | number>({ label, value, options, onChange, mono = false }: {
  label: string; value: T; options: { value: T; label: string }[]; onChange: (v: T) => void; mono?: boolean;
}) {
  return (
    <div role="group" aria-label={label} className={s.segment} data-mono={mono || undefined}>
      {options.map((o) => (
        <button key={String(o.value)} type="button" aria-pressed={o.value === value} onClick={() => onChange(o.value)}>{o.label}</button>
      ))}
    </div>
  );
}

/** One preference: what it is called, the control, and a line saying what it buys you. */
function Row({ label, hint, children }: { label: ReactNode; hint?: ReactNode; children: ReactNode }) {
  const id = useId();
  return (
    <div className={s.row} role="group" aria-labelledby={id}>
      <div id={id} className={s.rowLabel}>{label}</div>
      <div className={s.control}>{children}{hint ? <span className={s.hint}>{hint}</span> : null}</div>
    </div>
  );
}

/** One card of the sheet: a heading, a line on what it holds, then its rows. */
function Section({ title, children }: { title: string; children: ReactNode }) {
  const id = useId();
  return (
    <section aria-labelledby={id} className={s.card}>
      <div className={s.cardHead}>
        <h3 id={id} className={s.title}>{title}</h3>
      </div>
      {children}
    </section>
  );
}

const SIZES = ["12", "13", "14", "16", "18"];
const TABS = [2, 4, 8].map((n) => ({ value: n, label: String(n) }));

/** How the editor is set, and whether the clock is on screen. Every row is a preference of
 *  this browser: none of it is in your progress, and none of it travels in a backup. */
function EditorSettings() {
  const prefs = usePrefs();
  // the pane width belongs to the task screen's drag handle, so it is no editor setting
  const untouched = JSON.stringify({ ...prefs, taskPanePercent: 0 }) === JSON.stringify({ ...DEFAULTS, taskPanePercent: 0 });
  return (
    <Section title="Editor">
      <Row label="Font">
        <Select value={prefs.font} ariaLabel="Editor font" className={s.fontSelect}
          options={FONTS.map((f) => ({ value: f.value, label: f.label }))}
          onChange={(v) => setPrefs({ font: v as typeof prefs.font })} />
      </Row>
      <Row label="Font size">
        <Select value={String(prefs.fontSize)} options={SIZES.map((n) => ({ value: n, label: `${n} px` }))} ariaLabel="Editor font size"
          onChange={(v) => setPrefs({ fontSize: Number(v) })} className={s.numberSelect} />
      </Row>
      <Row label="Font ligatures">
        <Toggle checked={prefs.ligatures} label={prefs.ligatures ? "On" : "Off"}
          onChange={(on) => setPrefs({ ligatures: on })} />
      </Row>
      <Row label="Key binding" hint={<span>Ctrl+Enter runs and Ctrl+Shift+Enter submits whichever you pick, and <kbd>C-g</kbd> always gets you out of a half-typed Emacs chord.</span>}>
        <Choice label="Key binding" value={prefs.keys}
          options={[{ value: "regular", label: "Standard" }, { value: "vim", label: "Vim" }, { value: "emacs", label: "Emacs" }]}
          onChange={(keys) => setPrefs({ keys })} />
      </Row>
      <Row label="Tab size">
        <Choice label="Tab size" value={prefs.tabSize} options={TABS} mono onChange={(tabSize) => setPrefs({ tabSize })} />
      </Row>
      <Row label="Word wrap" hint="Off puts long lines behind a horizontal scrollbar.">
        <Toggle checked={prefs.wordWrap} label={prefs.wordWrap ? "On" : "Off"}
          onChange={(on) => setPrefs({ wordWrap: on })} />
      </Row>
      <Row label="Relative line numbers" hint="Counts from the cursor.">
        <Toggle checked={prefs.relativeLines} label={prefs.relativeLines ? "On" : "Off"}
          onChange={(on) => setPrefs({ relativeLines: on })} />
      </Row>
      <Row label="Practice timer" hint="Hidden or not, the time is still counted.">
        <Choice label="Practice timer" value={prefs.showTimer ? "shown" : "hidden"}
          options={[{ value: "shown", label: "Shown" }, { value: "hidden", label: "Hidden" }]}
          onChange={(v) => setPrefs({ showTimer: v === "shown" })} />
      </Row>
      {untouched ? null : (
        <div className={s.defaults}>
          <Button variant="quiet" onClick={() => setPrefs({ ...DEFAULTS, taskPanePercent: prefs.taskPanePercent })}><Icon name="Reset" />Restore to defaults</Button>
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

      <Section title="Your data">
        {pathError ? <EmptyState message={`Could not load settings: ${pathError}`} /> : paths ? (
          <div className={s.places}>
            <Location label="Data folder" icon="Folder" path={paths.root} />
            <Location label="Progress" icon="DataBase" path={paths.progress} />
            <Location label="Tasks" icon="Folder" path={paths.tasks} />
          </div>
        ) : <EmptyState message="Loading…" align="left" />}
      </Section>

      <div className={s.pair}>
        <Section title="Back up">
          <p className={s.text}>One file holding your cards, notes, log, archive and the code saved in every task.</p>
          <a href="/api/backup" download className={s.small} data-big=""><Icon name="Download" size={14} />Download a backup</a>
        </Section>

        <Section title="Restore">
          <p className={s.text}>You see what the file brings and what it replaces before anything is touched.</p>
          <label className={s.small} data-big="" data-busy={busy || undefined}>
            <Icon name="Upload" size={14} />Choose a backup file
            <input ref={picker} type="file" accept=".zip,application/zip" disabled={busy} aria-label="Choose a backup file to restore"
              onChange={(e) => choose(e.target.files?.[0] ?? null)} className={s.picker} />
          </label>
          {error ? <NoticeBanner message={error} /> : null}
          {preview ? (
            <div className={s.result}>
              <div>Taken {preview.created?.replace("T", " at ") ?? "at an unknown time"} on drillion v{preview.drillion}.</div>
              <div>Brings back {counts(preview.brings)}.</div>
              <div className={s.text}>
                Replaces {preview.replaces.cards} cards, {preview.replaces.archive} solved tasks
                and {preview.replaces.notes} notes you have now. What it replaces is written to a backup of its own first.
              </div>
              {preview.unknown.length ? (
                <NoticeBanner message={`${preview.unknown.length} task${preview.unknown.length > 1 ? "s" : ""} in this backup are not in this version of drillion, so their saved code stays in the file: ${preview.unknown.join(", ")}`} />
              ) : null}
              <div className={s.actions}>
                <Button variant="primary" disabled={busy} onClick={apply}>Replace my data</Button>
                <Button variant="quiet" disabled={busy} onClick={() => choose(null)}>Cancel</Button>
              </div>
            </div>
          ) : null}
          {done ? (
            <div className={s.result}>
              <div><Icon name="CheckmarkOutline" />Restored {counts(done.brings)}.</div>
              <div className={s.kept}><Icon name="Archive" />What you had before is at <code>{done.kept}</code>.</div>
              <div><Button onClick={() => { location.hash = "#/"; location.reload(); }}><Icon name="ArrowLeft" />Back to the catalogue</Button></div>
            </div>
          ) : null}
        </Section>
      </div>

      <DangerZone />
    </div>
  );
}
