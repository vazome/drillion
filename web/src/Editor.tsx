import { useEffect, useRef, useState, type CSSProperties } from "react";
import * as monaco from "@codingame/monaco-vscode-editor-api";
// the extension API, for the one thing the editor API cannot do: publish a diagnostic the
// editor renders exactly as it renders the language server's
import * as vscode from "vscode";
import type { Meta } from "./api";
// classic mode highlights with Monarch, and the editor API ships no grammars. The package
// index pulls all ~90 languages; drillion takes only the ones a task artifact is written in.
import "@codingame/monaco-vscode-standalone-languages/languages/definitions/python/register.js";
import "@codingame/monaco-vscode-standalone-languages/languages/definitions/yaml/register.js";
import "@codingame/monaco-vscode-standalone-languages/languages/definitions/dockerfile/register.js";
import { EditorApp } from "monaco-languageclient/editorApp";
import { MonacoVscodeApiWrapper } from "monaco-languageclient/vscodeApiWrapper";
import { LanguageClientWrapper } from "monaco-languageclient/lcwrapper";
import { configureDefaultWorkerFactory } from "monaco-languageclient/workerFactory";
import { initVimMode } from "monaco-vim";
import { EmacsExtension } from "monaco-emacs";
import { DEFAULTS, fontStack, type Prefs } from "./prefs";
import "./Editor.css";

// Every mono face is `font-display: swap`, and Monaco measures the character advance once
// at construction: an editor built before the woff2 lands keeps drawing the caret and the
// selection on the fallback's grid, drifting further off the longer the line. This is also
// what a font picked in Settings needs, since that face loads the moment it is chosen.
document.fonts.addEventListener("loadingdone", () => monaco.editor.remeasureFonts());

const token = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const bare = (name: string) => token(name).replace("#", "");

/** The page only ever holds one task's region, so one file is all the server is ever told
 *  about. `/workspace` is a placeholder the bridge swaps for the real tasks directory: a
 *  browser has no business knowing filesystem paths. */
const WORKSPACE = "file:///workspace";
// Monaco reads the language off the extension, so naming the file is choosing the mode.
const EXT: Partial<Record<Meta["kind"], string>> = { python: "py", docker: "dockerfile" };
const ext = (kind: Meta["kind"]) => EXT[kind] ?? "yaml";
const fileFor = (kind: Meta["kind"]) => `${WORKSPACE}/${kind === "python" ? "solve" : "task"}.${ext(kind)}`;

/** wss on a served-over-TLS page: a tunnel or a reverse proxy in front of drillion makes a
 *  plain ws:// socket mixed content, which the browser blocks outright. */
const socketUrl = () =>
  `${location.protocol === "https:" ? "wss:" : "ws:"}//${location.host}/lsp`;

/** The vscode API may be started once per page — it owns global state, not per-component
 *  state. A rejection is deliberately not cached: a first failure must not blank every
 *  editor for the life of the page. Classic mode keeps `defineTheme` working, which is
 *  what lets the editor wear the design tokens. */
let api: Promise<void> | undefined;
function startApi() {
  return (api ??= new MonacoVscodeApiWrapper({
    $type: "classic",
    viewsConfig: { $type: "EditorService" },
    // VS Code's own themes would win over `defineTheme`, and the tokens are the point
    advanced: { loadThemes: false },
    monacoWorkerFactory: configureDefaultWorkerFactory,
  })
    .start()
    .catch((err) => {
      api = undefined;
      throw err;
    }));
}

/** Completions are a bonus, never a gate: a language server that is down, slow or missing
 *  must still leave a working editor behind, so this is started beside the editor rather
 *  than in front of it. */
let client: Promise<void> | undefined;
function startLanguageClient() {
  client ??= new LanguageClientWrapper({
    languageId: "python",
    connection: { options: { $type: "WebSocketUrl", url: socketUrl() } },
    clientOptions: {
      documentSelector: ["python"],
      workspaceFolder: { index: 0, name: "workspace", uri: monaco.Uri.parse(WORKSPACE) },
    },
  })
    .start()
    .catch((err: unknown) => {
      console.error("no language server; editing still works", err);
    });
}

/** One theme, redefined per mode: Monaco themes are global and named, so the dark toggle
 *  rewrites `drillion` rather than swapping between two. Rule colours are bare hex. */
function applyTheme(dark: boolean) {
  monaco.editor.defineTheme("drillion", {
    base: dark ? "vs-dark" : "vs",
    inherit: true,
    rules: [
      { token: "keyword", foreground: bare("--syn-keyword"), fontStyle: "bold" },
      { token: "string", foreground: bare("--syn-string") },
      { token: "number", foreground: bare("--syn-number") },
      { token: "comment", foreground: bare("--syn-comment"), fontStyle: "italic" },
      { token: "identifier", foreground: bare("--text") },
      { token: "type.identifier", foreground: bare("--syn-function"), fontStyle: "bold" },
    ],
    colors: {
      "editor.background": token("--editor"),
      "editor.foreground": token("--text"),
      "editorCursor.foreground": token("--accent"),
      "editor.selectionBackground": token("--accent-tint"),
      "editor.lineHighlightBackground": token("--surface-2"),
      "editorLineNumber.foreground": token("--text-faint"),
      "editorLineNumber.activeForeground": token("--text-muted"),
      "editorGutter.background": token("--gutter"),
      "editorHoverWidget.background": token("--surface"),
      "editorHoverWidget.foreground": token("--text"),
      "editorHoverWidget.border": token("--border-strong"),
      // accent on both sides: pass/fail already mean the tests, and the left pane is code
      // that passed
      "diffEditor.insertedLineBackground": token("--accent-tint"),
      "diffEditor.removedLineBackground": token("--accent-tint"),
      "diffEditor.insertedTextBackground": token("--accent-line"),
      "diffEditor.removedTextBackground": token("--accent-line"),
    },
  });
  monaco.editor.setTheme("drillion");
}

const editorOptions: monaco.editor.IStandaloneEditorConstructionOptions = {
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  automaticLayout: true,
  // the frame clips for its rounded corners, and suggest/hover/signature panels render
  // inside the editor by default — this reparents them so they are not cut off
  fixedOverflowWidgets: true,
};

/** The half of the editor's setup Settings owns. Applied at construction and again on every
 *  change, so a preference edited while a task is open lands on the editor already there. */
const looks = (p: Prefs): monaco.editor.IEditorOptions & monaco.editor.IGlobalEditorOptions => ({
  fontFamily: fontStack(p.font),
  fontSize: p.fontSize,
  fontLigatures: p.ligatures,
  tabSize: p.tabSize,
  detectIndentation: false, // or the stub's own indentation decides, and the setting does nothing
  wordWrap: p.wordWrap ? "on" : "off",
  lineNumbers: p.relativeLines ? "relative" : "on",
});

const frame = {
  border: "1px solid var(--border)",
  borderRadius: "var(--radius)",
  overflow: "hidden",
};

/** The binding's own line: Vim's mode, pending keys and `:` prompt, or the keys Emacs is
 *  still waiting on. It has to be a real element outside the editor, so the binding has
 *  somewhere to render and the editor keeps its full height. */
const statusStyle: CSSProperties = {
  height: 22, display: "flex", alignItems: "center", padding: "0 10px",
  font: "var(--fs-sm)/22px var(--font-mono)", fontSize: 12,
  color: "var(--text-muted)", background: "var(--surface-2)",
  borderTop: "1px solid var(--border)",
};

/** A failed editor says so. Blank boxes are the one outcome worth ruling out: the learner
 *  cannot tell them from a task with nothing in it. */
function Failed({ height }: { height: string }) {
  return (
    <div style={{
      height, display: "grid", placeItems: "center", padding: "1rem", textAlign: "center",
      color: "var(--text-muted)", fontSize: "var(--fs-sm)", background: "var(--editor)", ...frame,
    }}>
      The editor failed to load. Reload the page; if it keeps happening the browser console
      has the reason.
    </div>
  );
}

export function Editor({ kind, value, onChange, onRun, onSubmit, readOnly, dark, height, prefs, problem }: {
  kind: Meta["kind"]; value: string; onChange: (v: string) => void; onRun: () => void; onSubmit: () => void;
  readOnly?: boolean; dark: boolean; height: string; prefs: Prefs;
  problem?: { message: string; line: number | null } | null;
}) {
  const host = useRef<HTMLDivElement>(null);
  const status = useRef<HTMLDivElement>(null);
  const app = useRef<EditorApp>(null);
  const marks = useRef<vscode.DiagnosticCollection | null>(null);
  const [failed, setFailed] = useState(false);
  const [pending, setPending] = useState("");   // Emacs's half-typed chord
  // a key binding needs the editor instance, which only exists once `start()` resolved
  const [ready, setReady] = useState(false);
  // the editor is built once, so construction reads the preferences of that moment; the
  // effect below owns every later change
  const first = useRef(prefs);
  // the editor reads these when the user acts, so it must never close over a stale one
  const latest = useRef({ onChange, onRun, onSubmit });
  useEffect(() => { latest.current = { onChange, onRun, onSubmit }; }, [onChange, onRun, onSubmit]);

  useEffect(() => {
    let live = true;
    let started: EditorApp | undefined;
    startApi()
      .then(() => {
        if (!live || !host.current) return;
        applyTheme(dark);
        // `documentSelector: ["python"]` already keeps the server off a YAML model, so this
        // is about not opening a socket a manifest-only session never needs.
        if (kind === "python") startLanguageClient();
        started = app.current = new EditorApp({
          id: "solve",
          codeResources: { modified: { text: value, uri: fileFor(kind) } },
          editorOptions: { ...editorOptions, ...looks(first.current) },
        });
        started.registerOnTextChangedCallback((t) => latest.current.onChange(t.modified ?? ""));
        return started.start(host.current);
      })
      .then(() => {
        const editor = started?.getEditor();
        editor?.addCommand(
          monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
          () => latest.current.onRun(),
        );
        // Submit is the committing chord, so it wears the modifier Run does not
        editor?.addCommand(
          monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter,
          () => latest.current.onSubmit(),
        );
        if (live && editor) setReady(true);
      })
      .catch((err: unknown) => {
        console.error("editor failed to start", err);
        if (live) setFailed(true);
      });
    return () => {
      live = false;
      app.current = null;
      void started?.dispose();
    };
  }, [kind]); // eslint-disable-line react-hooks/exhaustive-deps

  // `value` is also the truth after a reset or a 409, so push it when it drifts
  useEffect(() => {
    const current = app.current?.getTextModels().modified?.getValue();
    if (current !== undefined && current !== value) app.current?.updateCode({ modified: value });
  }, [value, ready]);

  useEffect(() => { app.current?.getEditor()?.updateOptions({ readOnly: !!readOnly }); }, [readOnly, ready]);
  useEffect(() => { app.current?.getEditor()?.updateOptions(looks(prefs)); }, [prefs, ready]);

  /** The server owns the only parser that can refuse a save, so its refusal is a diagnostic
   *  like any other and is published the way a language server publishes its own. That is
   *  the whole point of the collection: going through the same channel is what makes the
   *  editor draw it in VS Code's own shape, with the severity colour, the `source` suffix,
   *  the Problems entry and the Quick Fix bar, and stack it in one hover beside whatever
   *  the language server reported on the same line. Drawing it as a decoration with a
   *  hand-written hover instead produces a panel that only resembles one.
   *
   *  `monaco.editor.setModelMarkers` is the other obvious route and silently does nothing
   *  here: the editor builds its models through the vscode API's model references, which
   *  monaco's standalone marker registry never sees.
   *
   *  Diagnostics are never fatal. A vscode API that failed to start leaves an editor that
   *  still edits, which is the same bargain the language server is held to.
   *
   *  A refusal that names no line still has to be visible, so it marks the last line rather
   *  than going quiet. The collection holds one file at a time, so clearing it first also
   *  retires the diagnostic left on the other kind's URI when a task swaps the model. */
  useEffect(() => {
    const model = app.current?.getEditor()?.getModel();
    if (!model) return;
    try {
      marks.current ??= vscode.languages.createDiagnosticCollection("drillion");
    } catch (err) {
      console.error("diagnostics unavailable", err);
      return;
    }
    marks.current.clear();
    if (!problem) return;
    const last = model.getLineCount();
    const line = problem.line && problem.line >= 1 && problem.line <= last ? problem.line : last;
    // vscode counts lines and characters from zero; monaco counts both from one
    const found = new vscode.Diagnostic(
      new vscode.Range(
        line - 1, (model.getLineFirstNonWhitespaceColumn(line) || 1) - 1,
        line - 1, model.getLineMaxColumn(line) - 1,
      ),
      problem.message,
      vscode.DiagnosticSeverity.Error,
    );
    found.source = "drillion";
    marks.current.set(vscode.Uri.parse(model.uri.toString()), [found]);
  }, [problem, value, ready, kind]);

  useEffect(() => () => { marks.current?.dispose(); marks.current = null; }, []);
  // waits for the API rather than testing it: `api` is truthy while still pending, and
  // theming early touches Monaco's standalone services, which makes `start()` throw
  useEffect(() => { void api?.then(() => applyTheme(dark)).catch(() => {}); }, [dark]);

  // Vim, attached and detached without rebuilding the editor: the binding only ever reads
  // and writes through the editor instance, so the model, the draft and the undo stack all
  // survive a learner changing their mind. Turning it off leaves a plain editor behind.
  const keys = prefs.keys;
  useEffect(() => {
    const editor = app.current?.getEditor();
    if (keys === "regular" || !ready || !editor || !status.current) return;
    if (keys === "vim") {
      const mode = initVimMode(editor, status.current);
      return () => mode.dispose();
    }
    // Emacs reports its pending prefix as an event rather than owning a node, so the line
    // is written here. C-g clears it, which is the binding's own way out of a half-typed
    // chord and the reason it is never a trap.
    const emacs = new EmacsExtension(editor);
    emacs.onDidChangeKey(setPending);
    emacs.start();
    return () => { emacs.dispose(); setPending(""); };
  }, [keys, ready]);

  if (failed) return <Failed height={height} />;
  return (
    <div style={{ display: "flex", flexDirection: "column", height, background: "var(--editor)" }}>
      <div ref={host} style={{ flex: 1, minHeight: 0, fontSize: prefs.fontSize }} />
      {/* always mounted, so the binding has a node the moment it is switched on */}
      <div ref={status} style={{ ...statusStyle, display: keys === "regular" ? "none" : "flex" }}>
        {keys === "emacs" ? pending : null}
      </div>
    </div>
  );
}

/** Two read-only panes with the changed lines marked: what the learner wrote on the left,
 *  the reference on the right. Shares the editor's theme, so the two read as one surface. */
export function DiffView({ kind, mine, reference, dark, maxHeight, prefs = DEFAULTS, sideBySide = true, onChanges, unframed = false }: {
  kind: Meta["kind"]; mine: string; reference: string; dark: boolean; maxHeight: string; prefs?: Prefs;
  /** false draws one pane with the changes inline */
  sideBySide?: boolean;
  /** told how many lines differ, each time the diff is worked out */
  onChanges?: (lines: number) => void;
  /** no frame of its own, for a pane that is already one */
  unframed?: boolean;
}) {
  const host = useRef<HTMLDivElement>(null);
  const app = useRef<EditorApp>(null);
  const [failed, setFailed] = useState(false);
  const [ready, setReady] = useState(false);
  // built once per kind, as the editor is: the effects below carry every later change
  const first = useRef({ mine, reference, dark, prefs, sideBySide });
  const told = useRef(onChanges);
  useEffect(() => { told.current = onChanges; }, [onChanges]);

  useEffect(() => {
    let live = true;
    let started: EditorApp | undefined;
    startApi()
      .then(() => {
        if (!live || !host.current) return;
        const at = first.current;
        applyTheme(at.dark);
        started = app.current = new EditorApp({
          id: "diff",
          useDiffEditor: true,
          readOnly: true,
          codeResources: {
            original: { text: at.mine, uri: `${WORKSPACE}/mine.${ext(kind)}` },
            modified: { text: at.reference, uri: `${WORKSPACE}/reference.${ext(kind)}` },
          },
          diffEditorOptions: {
            ...editorOptions, ...looks(at.prefs), readOnly: true, renderSideBySide: at.sideBySide,
            // Monaco drops to an inline diff below 900px and this pane is narrower than
            // that, which would contradict the "yours on the left, the reference on the
            // right" copy sitting directly above it
            renderSideBySideInlineBreakpoint: 0,
          },
        });
        return started.start(host.current);
      })
      .then(() => {
        if (!live || !started) return;
        const diff = started.getDiffEditor();
        // a change spans the longer of its two sides: 3 lines replaced by 1 is 3 lines differing
        diff?.onDidUpdateDiff(() => told.current?.((diff.getLineChanges() ?? []).reduce((n, c) =>
          n + Math.max(c.originalEndLineNumber ? c.originalEndLineNumber - c.originalStartLineNumber + 1 : 0,
            c.modifiedEndLineNumber ? c.modifiedEndLineNumber - c.modifiedStartLineNumber + 1 : 0), 0)));
        setReady(true);
      })
      .catch((err: unknown) => {
        console.error("diff failed to start", err);
        if (live) setFailed(true);
      });
    return () => {
      live = false;
      app.current = null;
      setReady(false);
      void started?.dispose();
    };
  }, [kind]);

  useEffect(() => {
    const models = app.current?.getTextModels();
    if (!models) return;
    if (models.original?.getValue() !== mine) app.current?.updateCode({ original: mine });
    if (models.modified?.getValue() !== reference) app.current?.updateCode({ modified: reference });
  }, [mine, reference, ready]);

  useEffect(() => { app.current?.getDiffEditor()?.updateOptions({ ...looks(prefs), renderSideBySide: sideBySide }); }, [prefs, sideBySide, ready]);
  useEffect(() => { void api?.then(() => applyTheme(dark)).catch(() => {}); }, [dark]);

  if (failed) return <Failed height={maxHeight} />;
  return <div ref={host} style={{ height: maxHeight, fontSize: prefs.fontSize, ...(unframed ? {} : frame) }} />;
}
