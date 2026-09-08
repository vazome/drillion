import { useEffect, useRef, useState } from "react";
import { Button, Card, EmptyState, Input, NoticeBanner, Toggle } from "./ds/index.js";
import { api, type Paths, type Bundle, type Erased, type Restored } from "./api";
import { setVimMode, vimMode } from "./editorMode";

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
          <div><Button onClick={() => location.assign("#/")}>Back to the catalogue</Button></div>
        </div>
      ) : null}
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
  const [vim, setVim] = useState(vimMode);
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
    <div style={{ maxWidth: 820, margin: "0 auto", display: "grid", gap: 18 }}>
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

      <Card label="Editor">
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <Toggle
            checked={vim}
            onChange={(on) => { setVimMode(on); setVim(on); }}
            label={vim ? "Vim keys" : "Regular keys"}
          />
          <span style={{ fontSize: 14, color: "var(--text-muted)" }}>
            {vim
              ? "Modal editing, with the mode shown under the editor. Turn this off to go back to ordinary typing."
              : "Ordinary typing. Turn this on if you use Vim motions everywhere else."}
          </span>
        </div>
        <p style={{ margin: "10px 0 0", fontSize: 13, color: "var(--text-faint)" }}>
          Ctrl+Enter still runs and Ctrl+Shift+Enter still submits, in either mode. This
          setting lives in this browser, so it is not part of a backup.
        </p>
      </Card>

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
          Restoring replaces your current progress and the code saved in every task. What it
          replaces is written to a backup of its own first, so you can undo it.
        </p>
        <input
          ref={picker} type="file" accept=".zip,application/zip" disabled={busy}
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
            {done.failed.length ? <NoticeBanner message={`The code could not be written back for: ${done.failed.join(", ")}`} /> : null}
            <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
              What you had before is at <code>{done.kept}</code>.
            </div>
            <div><Button onClick={() => location.assign("#/")}>Back to the catalogue</Button></div>
          </div>
        ) : null}
      </Card>

      <DangerZone />
    </div>
  );
}
