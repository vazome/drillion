import { useEffect, useRef, useState } from "react";
import * as monaco from "@codingame/monaco-vscode-editor-api";
// classic mode highlights with Monarch, and the editor API ships no grammars. The package
// index pulls all ~90 languages; drillion is a Python trainer, so it takes the one.
import "@codingame/monaco-vscode-standalone-languages/languages/definitions/python/register.js";
import { EditorApp } from "monaco-languageclient/editorApp";
import { MonacoVscodeApiWrapper } from "monaco-languageclient/vscodeApiWrapper";
import { LanguageClientWrapper } from "monaco-languageclient/lcwrapper";
import { configureDefaultWorkerFactory } from "monaco-languageclient/workerFactory";

const token = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const bare = (name: string) => token(name).replace("#", "");

/** The page only ever holds one task's region, so one file is all the server is ever told
 *  about. `/workspace` is a placeholder the bridge swaps for the real tasks directory: a
 *  browser has no business knowing filesystem paths. */
const WORKSPACE = "file:///workspace";
const FILE = `${WORKSPACE}/solve.py`;

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
  fontFamily: token("--font-mono"),
  fontSize: parseInt(token("--fs-code")) || 13,
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  wordWrap: "on",
  tabSize: 4,
  automaticLayout: true,
  // the frame clips for its rounded corners, and suggest/hover/signature panels render
  // inside the editor by default — this reparents them so they are not cut off
  fixedOverflowWidgets: true,
};

const frame = {
  border: "1px solid var(--border)",
  borderRadius: "var(--radius)",
  overflow: "hidden",
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

export function Editor({ value, onChange, onRun, onSubmit, readOnly, dark, height }: {
  value: string; onChange: (v: string) => void; onRun: () => void; onSubmit: () => void;
  readOnly?: boolean; dark: boolean; height: string;
}) {
  const host = useRef<HTMLDivElement>(null);
  const app = useRef<EditorApp>(null);
  const [failed, setFailed] = useState(false);
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
        startLanguageClient();
        started = app.current = new EditorApp({
          id: "solve",
          codeResources: { modified: { text: value, uri: FILE } },
          editorOptions,
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
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // `value` is also the truth after a reset or a 409, so push it when it drifts
  useEffect(() => {
    const current = app.current?.getTextModels().modified?.getValue();
    if (current !== undefined && current !== value) app.current?.updateCode({ modified: value });
  }, [value]);

  useEffect(() => { app.current?.getEditor()?.updateOptions({ readOnly: !!readOnly }); }, [readOnly]);
  // waits for the API rather than testing it: `api` is truthy while still pending, and
  // theming early touches Monaco's standalone services, which makes `start()` throw
  useEffect(() => { void api?.then(() => applyTheme(dark)).catch(() => {}); }, [dark]);

  if (failed) return <Failed height={height} />;
  return <div ref={host} style={{ height, fontSize: "var(--fs-code)", ...frame }} />;
}

/** Two read-only panes with the changed lines marked: what the learner wrote on the left,
 *  the reference on the right. Shares the editor's theme, so the two read as one surface. */
export function DiffView({ mine, reference, dark, maxHeight }: {
  mine: string; reference: string; dark: boolean; maxHeight: string;
}) {
  const host = useRef<HTMLDivElement>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let live = true;
    let started: EditorApp | undefined;
    startApi()
      .then(() => {
        if (!live || !host.current) return;
        applyTheme(dark);
        started = new EditorApp({
          id: "diff",
          useDiffEditor: true,
          readOnly: true,
          codeResources: {
            original: { text: mine, uri: "file:///workspace/mine.py" },
            modified: { text: reference, uri: "file:///workspace/reference.py" },
          },
          diffEditorOptions: {
            ...editorOptions, readOnly: true, renderSideBySide: true,
            // Monaco drops to an inline diff below 900px and this pane is narrower than
            // that, which would contradict the "yours on the left, the reference on the
            // right" copy sitting directly above it
            renderSideBySideInlineBreakpoint: 0,
          },
        });
        return started.start(host.current);
      })
      .catch((err: unknown) => {
        console.error("diff failed to start", err);
        if (live) setFailed(true);
      });
    return () => {
      live = false;
      void started?.dispose();
    };
  }, [mine, reference, dark]);

  if (failed) return <Failed height={maxHeight} />;
  return <div ref={host} style={{ height: maxHeight, fontSize: "var(--fs-code)", ...frame }} />;
}
