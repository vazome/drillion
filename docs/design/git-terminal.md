# Design handover: the git terminal

One component for the task page (`#/task/:slug`), to be drawn in Claude Design and vendored into
`web/src/ds/` like the rest of the Mineral Blue system. [`DESIGN.md`](../../DESIGN.md) is the
product brief, [`CONTEXT.md`](../../CONTEXT.md) the vocabulary, and the concept this serves is
[`2026-09-26-git-track-design.md`](../superpowers/specs/2026-09-26-git-track-design.md).

## Why it is needed

drillion is adding git tasks. A git task is a repository in a state, and a spec saying what
state it should be in. The learner practises the way they would at their desk: a real `bash`,
real `git`, and `nano` or `vim` when git opens an editor for a commit message, a rebase or a
conflict. Nothing is typed into Monaco. When they press Run or Submit, drillion grades the
repository they left behind.

Today the task page has one work surface, the editor. On a git task a terminal takes its place.

## What exists

- The design system: `web/src/ds/`, plain React components over CSS custom properties with
  sibling CSS Modules, no Tailwind, no component library. Tokens in `web/src/ds/tokens/*.css`
  (both themes, IBM Plex Sans / Spline Sans Mono, spacing, motion). Closest relatives:
  `FileTabs.jsx` (a strip that sits flush above the work surface), `Collapsible.jsx`.
- The task page (`web/src/Task.tsx`), editor side, top to bottom:
  1. a toolbar row: `attempt N`, `seed N`, a right-aligned status line in `--warn`, and Abandon;
  2. the Monaco editor, `clamp(280px, 42vh, 560px)` tall for non-Python tasks, themed from
     the same tokens;
  3. Run and Submit, then the Result card: a banner, the grader's messages, then collapsibles.
- The server side is built: a WebSocket per task at `/terminal/<slug>` running a sandboxed
  bash in the task's repository, and `POST /api/task/<slug>/repo/reset`.

## What to draw: `Terminal`

The terminal emulator is xterm.js (`@xterm/xterm` 6 with `@xterm/addon-fit`), the one VS Code
uses. Drawing it means its frame, its theme and its states, not a terminal emulator.

**Props**

```ts
slug: string                         // the task; the socket is /terminal/<slug>
dark: boolean                        // which theme the page is in
live: boolean                        // an attempt is open and not yet passed
onClosed?: (code: number) => void    // the socket closed, with its close code
```

**The contract with the server** (already built, and all there is):

- Open `ws://<host>/terminal/<slug>` (`wss://` on a page served over TLS) while `live` is true;
  close it when `live` turns false or the component unmounts.
- Page to server, text frames of JSON: `{"i": "<data>"}` for every xterm `onData`, and
  `{"r": [cols, rows]}` after every fit: on open, and whenever the box changes size.
- Server to page, binary frames: bytes to hand to `terminal.write` as they arrive. The first
  line is drillion's own, saying how the shell is confined.

**The theme**

Background `--surface`, foreground `--text`, cursor `--accent`, selection `--accent-tint`, the
mono face at the editor's size. The 16 ANSI colours are the real work: `git status`, `git diff`,
`git log --graph` and the prompt all use them, and each has to read on both themes' background
at WCAG AA. Red and green carry meaning in git's output (removed and added), so keep them
recognisably red and green, but calm, drillion's own, never a black and neon-green hacker look.

**States**

- **Connecting.** Brief, quiet.
- **Live.** The shell, filling the editor's box.
- **Closed 4000: moved to another tab.** The newer tab owns the shell. Say so in words and offer
  Reconnect.
- **Closed 4001: repository reset.** Reconnects by itself; the learner asked for this.
- **Closed 1013: too many terminals.** Four are open across tabs; ask them to close one.
- **Closed 1011: could not start.** The server has already written why on screen; offer Retry.
- **Not live.** No attempt is open, or the task was just passed: the last output stays visible,
  dimmed, with no cursor.
- **Offline.** The page lost the server.

**Reset repository**

A button in the toolbar row beside Abandon, with a confirm ("Put the repository back as the
task set it up? Your command history is kept."). It calls `POST /api/task/<slug>/repo/reset`;
the terminal then closes with 4001 and reconnects to a fresh repository.

**Where Run and Submit go.** They stay where they are for the other kinds. There is no editor
toolbar status line (nothing unsaved lives in the page); the toolbar keeps attempt, seed, Reset
repository and Abandon.

## Hard constraints

- Both themes from the tokens, with no colour that exists in only one.
- One new dependency, xterm.js with its fit addon, and nothing else.
- Keys belong to the shell. Escape, Tab, Ctrl-R, Ctrl-W, Ctrl-A, Ctrl-C, Ctrl-Z and the arrows
  all reach bash, nano or vim. The page keeps only its Submit shortcut; name which it is. Focus
  must still be able to leave the terminal by keyboard: show how.
- Calm, like the rest of drillion: no blinking banners, no colour-only meaning.
- Accessible: an accessible name ("Terminal, in the task's repository"), xterm.js's screen
  reader mode when one is in use, visible focus, the closed states said in words.
  `e2e/a11y.spec.ts` runs axe (WCAG A and AA, `color-contrast` included) in both themes and
  reflow at 200% zoom.
- `prefers-reduced-motion`: any transition collapses to nothing; the cursor does not blink.
- It is a terminal, not an IDE: no tabs of shells, no split panes, no file tree.

## Deliverable

- `Terminal.jsx` and `Terminal.module.css` in the `ds/` idiom (named export, props as above),
  with the socket wiring above inside it.
- One entry in `ds/index.d.ts` and one export in `ds/index.js`.
- The 16-colour palette and any new tokens added to `tokens/*.css`.
- A mock of the task page's editor column with it in place: live, showing `git status` with
  staged, unstaged and untracked files and a `git log --oneline --graph --all` with two branches
  and a merge; nano open on a commit message; closed with 4000. Each in light and dark.

Agents integrate it: rendering it in place of the editor when a task's kind is `git`, opening
the attempt before `live` turns true, the Reset repository call, and the Result card's "Your
repository" output, which reuses `Collapsible` and needs no new drawing.
