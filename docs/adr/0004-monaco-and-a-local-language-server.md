# Monaco and a local language server, so the editor can answer questions about the code

Typing `rows.` in a task offered nothing. `@codemirror/lang-python` completes names in scope,
builtins and snippets; attribute completion needs type inference, which CodeMirror has none of and
no plugin adds. The gap is not a missing setting — no editor completes `rows.` without something
that knows what `rows` is.

"Categorical pragmatism" says people are here to get better at Python and drillion's job is to aid
that. An editor that cannot say what a list can do is a worse tool for the one thing the project
exists for.

## Considered options

**A browser-side Pyright compiled to WebAssembly.** Real, and shipping: python.microbit.org runs
CodeMirror 6 with Pyright in a web worker, MIT, in production, for an audience much like ours. But
the browser builds are abandoned forks — `microbit-foundation/pyright` last moved in 2022,
`@typefox/pyright-browser` in 2023, against an upstream now far ahead. Taking this means owning a
fork of a type checker. Microsoft's own pyright-play.net does not do it either; it runs the server
in Node and talks to it over the network.

**ty or pyrefly compiled to WebAssembly.** Both very much alive, and `crates/ty_wasm` already
exposes completions, hover and signature help with typeshed vendored into the binary. Neither is
published to npm, so this means a Rust toolchain in the frontend build. Worth revisiting when one
of them ships a package.

**Pyodide with jedi.** A ~10 MB download to run an interpreter in the browser purely to introspect
a ten-line function, 3–5× slower than native, with weaker inference than Pyright. Rejected.

**A local language server behind a websocket.** Taken. drillion already runs a FastAPI server on
the learner's own machine and already executes their code there; a language server is one more
local subprocess, and nothing leaves the machine. It needs no WASM, no fork, and no build-time
toolchain.

The editor moves from CodeMirror 6 to Monaco with it. Monaco is VS Code's editor core and the
maintainer works in VS Code daily, so the editing model is the one already in hand. The cost is
real and worth naming: `monaco-languageclient` brings ~30 `@codingame/monaco-vscode-*` packages —
forks of VS Code internals — and the bundle goes from 275 KB to 3.7 MB gzipped. Served from
localhost, that buys latency nobody can perceive. On a public site it would not be defensible.

`$type: 'classic'` rather than `'extended'`: extended pulls VS Code's theme service, which
overrides `defineTheme` and would break the `--syn-*` match between the editor and the fenced code
in the spec pane. The design tokens win.

**basedpyright rather than jedi-language-server.** basedpyright installs 280 MB, 204 MB of it a
bundled Node runtime, against jedi's 35 MB of pure Python. Measured on drillion's own task shapes
they return the same completions, and jedi orders them better. basedpyright was taken for the
diagnostics: a learner writing a genuine type error should see it underlined, and jedi reports
none. A `docker run` image grows by the difference.

## Consequences

- **The region is the whole document the server sees.** The page only ever holds the learner's
  region; the machinery below the marker holds `_reference()`, which is the answer. All 172 regions
  are self-contained — checked by AST, none references a name it does not define — so the server
  loses nothing and the answer stays out of the browser.
- **A signature with no annotation still completes nothing.** Type inference needs a type to infer
  from. `def solve(rows):` yields zero completions from any language server; annotating the
  parameters is what makes this visible, and is a separate change.
- **A dead language server leaves a working editor.** The client starts beside the editor, never in
  front of it, and a failure to start says so on the page rather than rendering an empty box.
- **Monaco's editable element is a `div.native-edit-context`**, not a textarea and not
  contenteditable. Anything asking "is the user typing?" must name `.monaco-editor`; the `/`
  shortcut guard did not, and would have navigated away mid-edit.
