import React, { useEffect, useId, useRef, useState } from "react";
import { Terminal as XTerm } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "@xterm/xterm/css/xterm.css";
import { Button } from "./Button.jsx";
import { Icon } from "./Icon.jsx";
import s from "./Terminal.module.css";

/** The terminal a git task is worked in: a real bash in the task's repository, over a
 *  WebSocket, drawn by xterm.js. This component is the frame, the theme and the states; the
 *  shell and the repository are the server's.
 *
 *  Keys belong to the shell: Escape, Tab, Ctrl-R/W/A/C/Z and the arrows all reach bash, nano
 *  or vim. The page takes three chords the shell loses nothing by: Shift+Tab leaves the
 *  terminal (focus goes back to the head's actions, then Submit, which the page puts first in
 *  the DOM); Ctrl/⌘+Shift+Enter submits (a terminal sends it as plain Enter anyway); and, off a
 *  Mac, Ctrl+Shift+C / Ctrl+Shift+V copy and paste, as in VS Code's terminal. */

const LABEL = "Terminal, in the task's repository";
XTerm.strings.promptLabel = LABEL;

const MAC = typeof navigator !== "undefined" && /Mac|iPhone|iPad/.test(navigator.platform);

/** xterm's ITheme key for each of the 16 `--term-*` tokens. */
const ANSI = [
  ["black", "black"], ["red", "red"], ["green", "green"], ["yellow", "yellow"],
  ["blue", "blue"], ["magenta", "magenta"], ["cyan", "cyan"], ["white", "white"],
  ["brightBlack", "bright-black"], ["brightRed", "bright-red"], ["brightGreen", "bright-green"],
  ["brightYellow", "bright-yellow"], ["brightBlue", "bright-blue"], ["brightMagenta", "bright-magenta"],
  ["brightCyan", "bright-cyan"], ["brightWhite", "bright-white"],
];

/** Read the theme off the tokens, so both themes come from one place. A closed terminal
 *  sits on surface-2 with muted text and no cursor: dimmed, but still AA (every --term-*
 *  colour clears 4.5:1 on surface-2 too). */
function themeOf(el, idle) {
  const cs = getComputedStyle(el);
  const v = (name) => cs.getPropertyValue(name).trim();
  const ground = v(idle ? "--surface-2" : "--surface");
  const theme = {
    background: ground,
    foreground: v(idle ? "--text-muted" : "--text"),
    cursor: idle ? ground : v("--accent"),
    cursorAccent: ground,
    selectionBackground: v("--accent-tint"),
    selectionInactiveBackground: v("--surface-2"),
    scrollbarSliderBackground: v("--border-strong"),
    scrollbarSliderHoverBackground: v("--control-edge"),
    scrollbarSliderActiveBackground: v("--control-edge"),
  };
  for (const [key, token] of ANSI) theme[key] = v(`--term-${token}`);
  return theme;
}

/** What each close code means to the learner. Anything not named here is `closed`. */
const CLOSES = { 4000: "moved", 4001: "reset", 1013: "full", 1011: "failed", 1006: "offline" };

const STATE_WORD = {
  connecting: "Connecting…", live: "Live", reset: "Starting a fresh shell…",
  moved: "Closed", full: "Closed", failed: "Closed", closed: "Closed",
  offline: "Offline", idle: "Not running",
};

export function Terminal({ slug, dark, live, onClosed, actions, idleNote, fontFamily, fontSize = 14,
  screenReader = false, className, style }) {
  const host = useRef(null);
  const frame = useRef(null);
  const term = useRef(null);
  const fit = useRef(null);
  const sock = useRef(null);
  const [state, setState] = useState(live ? "connecting" : "idle");
  const [generation, setGeneration] = useState(0); // bumped to open a new socket
  const [wasLive, setWasLive] = useState(live);
  if (live !== wasLive) { setWasLive(live); if (live) setState("connecting"); }
  const howToLeave = useId();
  const closedCb = useRef(onClosed);
  useEffect(() => { closedCb.current = onClosed; });

  // one xterm for the life of the component
  useEffect(() => {
    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    const t = new XTerm({
      fontFamily: fontFamily || getComputedStyle(document.documentElement).getPropertyValue("--font-mono").trim() || "monospace",
      fontSize,
      lineHeight: 1.25,
      cursorStyle: "block",
      cursorInactiveStyle: "outline",
      cursorBlink: !reduced.matches,
      scrollback: 5000,
      // no contrast floor: every --term-* colour clears 4.5:1 on its own, and xterm 6 applies
      // the floor to reverse video wrongly (nano's title and key bars turn grey)
      minimumContrastRatio: 1,
      screenReaderMode: screenReader,
      macOptionIsMeta: true,
      smoothScrollDuration: 0,
      theme: themeOf(frame.current, !live),
    });
    const f = new FitAddon();
    t.loadAddon(f);
    t.open(host.current);
    t.textarea?.setAttribute("aria-label", LABEL);
    t.textarea?.setAttribute("aria-describedby", howToLeave);

    t.attachCustomKeyEventHandler((e) => {
      if (e.type !== "keydown") return true;
      const mod = MAC ? e.metaKey : e.ctrlKey;
      // Shift+Tab leaves: returning false lets the browser move focus back to Submit
      if (e.key === "Tab" && e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey) return false;
      // Submit belongs to the page; its listener sees the event bubble up
      if (e.key === "Enter" && mod && e.shiftKey) return false;
      // copy and paste off a Mac; on a Mac ⌘C and ⌘V never reach the shell anyway
      if (!MAC && e.ctrlKey && e.shiftKey && (e.code === "KeyC" || e.code === "KeyV")) return false;
      return true;
    });

    const send = (data) => {
      const ws = sock.current;
      if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ i: data }));
    };
    const onData = t.onData(send);
    const onBinary = t.onBinary(send);
    const onResize = t.onResize(({ cols, rows }) => {
      const ws = sock.current;
      if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ r: [cols, rows] }));
    });

    const box = new ResizeObserver(() => { try { f.fit(); } catch { /* not laid out yet */ } });
    box.observe(host.current);
    const motion = () => { t.options.cursorBlink = !reduced.matches; };
    reduced.addEventListener("change", motion);

    term.current = t;
    fit.current = f;
    return () => {
      reduced.removeEventListener("change", motion);
      box.disconnect();
      onData.dispose(); onBinary.dispose(); onResize.dispose();
      t.dispose();
      term.current = null;
    };
    // fontFamily/fontSize/screenReader are applied below without a new xterm
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // settings that can change under a running shell
  useEffect(() => {
    const t = term.current;
    if (!t) return;
    t.options.fontSize = fontSize;
    if (fontFamily) t.options.fontFamily = fontFamily;
    t.options.screenReaderMode = screenReader;
    try { fit.current.fit(); } catch { /* not laid out yet */ }
  }, [fontFamily, fontSize, screenReader]);

  // the theme follows the page; read after the page has swapped its class
  const idle = !live || (state !== "live" && state !== "connecting" && state !== "reset");
  useEffect(() => {
    const id = requestAnimationFrame(() => {
      const t = term.current;
      if (!t) return;
      t.options.theme = themeOf(frame.current, idle);
      t.options.disableStdin = idle;
      t.write(idle ? "\x1b[?25l" : "\x1b[?25h"); // hide the cursor while nothing listens
    });
    return () => cancelAnimationFrame(id);
  }, [dark, idle]);

  // the socket: open while live, closed when not
  useEffect(() => {
    if (!live) return; // the page shows "idle" whenever live is false
    const t = term.current;
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/terminal/${encodeURIComponent(slug)}`);
    ws.binaryType = "arraybuffer";
    sock.current = ws;
    let mine = true;

    ws.onopen = () => {
      if (!mine) return;
      // a second shell in the same scrollback starts on a line of its own
      if (t.buffer.active.cursorX > 0) t.write("\r\n");
      setState("live");
      try { fit.current.fit(); } catch { /* not laid out yet */ }
      ws.send(JSON.stringify({ r: [t.cols, t.rows] }));
    };
    ws.onmessage = (e) => {
      t.write(typeof e.data === "string" ? e.data : new Uint8Array(e.data));
    };
    ws.onclose = (e) => {
      if (sock.current === ws) sock.current = null;
      closedCb.current?.(e.code);
      if (!mine) return;
      const next = CLOSES[e.code] ?? (e.code === 1000 ? "idle" : "closed");
      if (next === "reset") {
        // the learner asked for this: mark the seam and come straight back
        t.write("\r\n\x1b[90m── repository reset: a fresh copy, same history ──\x1b[0m\r\n");
        setState("reset");
        setGeneration((g) => g + 1);
        return;
      }
      setState(!navigator.onLine ? "offline" : next);
    };

    return () => {
      mine = false;
      if (ws.readyState <= WebSocket.OPEN) ws.close(1000);
    };
  }, [slug, live, generation]);

  // lost the server: try again by itself, quietly, every few seconds and when the network
  // comes back; the learner did nothing to lose it
  useEffect(() => {
    if (state !== "offline") return;
    const again = () => setGeneration((g) => g + 1);
    const timer = setTimeout(again, 5000);
    addEventListener("online", again);
    return () => { clearTimeout(timer); removeEventListener("online", again); };
  }, [state, generation]);

  const retry = () => { setState("connecting"); setGeneration((g) => g + 1); };
  const notice = !live ? (idleNote ? { icon: "Information", text: idleNote } : null)
    : state === "moved" ? { icon: "Information", text: "This shell moved to a newer tab. Only one tab holds it at a time.", act: "Reconnect here" }
    : state === "full" ? { icon: "WarningAlt", text: "Four terminals are already open in other tabs. Close one of them, then try again.", act: "Try again" }
    : state === "failed" ? { icon: "WarningAlt", text: "The shell could not start. What went wrong is written above.", act: "Retry" }
    : state === "offline" ? { icon: "WarningAlt", text: "Lost the connection to drillion. It reconnects when the server is back.", act: "Reconnect" }
    : state === "closed" ? { icon: "Information", text: "The shell closed.", act: "Reconnect" }
    : null;

  return (
    <section ref={frame} aria-label={LABEL} data-state={live ? state : "idle"}
      className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <div className={s.head}>
        <span className={s.title}><Icon name="Terminal" />Terminal<span className={s.where}>in the task’s repository</span></span>
        <span className={s.state}>{STATE_WORD[live ? state : "idle"]}</span>
        <span className={s.grow} />
        <span className={s.leave} id={howToLeave}>
          <kbd aria-label="Shift Tab">⇧ Tab</kbd> leaves the terminal
        </span>
        {actions}
      </div>
      <div className={s.screen}>
        <div ref={host} className={s.host} />
      </div>
      <div role="status" className={s.foot}>
        {notice ? (<>
          <Icon name={notice.icon} className={s.footIcon} />
          <span className={s.footText}>{notice.text}</span>
          {notice.act ? <Button variant="secondary" onClick={retry}>{notice.act}</Button> : null}
        </>) : null}
      </div>
    </section>
  );
}
