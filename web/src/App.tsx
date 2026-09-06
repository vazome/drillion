import { useEffect, useState } from "react";
import { Toggle } from "./ds/index.js";
import { api, type Health } from "./api";
import { Catalogue } from "./Catalogue";
import { Task } from "./Task";
import { Progress } from "./Progress";
import { Deps } from "./Deps";

/** Hash routing, whole implementation. */
export function useHash() {
  const [hash, setHash] = useState(() => location.hash.slice(1) || "/");
  useEffect(() => {
    const on = () => setHash(location.hash.slice(1) || "/");
    addEventListener("hashchange", on);
    return () => removeEventListener("hashchange", on);
  }, []);
  return hash;
}

/** True while the keystroke belongs to something the user is typing in. */
function typing(el: EventTarget | null) {
  const node = el as HTMLElement | null;
  return !!node?.closest?.("input, textarea, select, [contenteditable='true'], .monaco-editor");
}

/** `/` anywhere goes to the catalogue and asks it, through the hash, for its search box. */
function useSlashToSearch() {
  useEffect(() => {
    const on = (e: globalThis.KeyboardEvent) => {
      if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey || e.isComposing || typing(e.target)) return;
      e.preventDefault();
      // replace on the catalogue itself, or Back gets an entry that goes nowhere
      if (location.hash === "#/") location.replace("#/?q"); else location.hash = "#/?q";
    };
    addEventListener("keydown", on);
    return () => removeEventListener("keydown", on);
  }, []);
}

/** Applied before first render as well as in the setter: the editor reads its colours
 * straight off these variables, so `.dark` must never be a frame behind. */
function applyTheme(dark: boolean) {
  document.documentElement.classList.toggle("dark", dark);
  localStorage.setItem("drillion-theme", dark ? "dark" : "light");
}
const savedTheme = localStorage.getItem("drillion-theme");
const initialDark = savedTheme ? savedTheme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
applyTheme(initialDark);

function useTheme(): [boolean, (v: boolean) => void] {
  const [dark, setDark] = useState(initialDark);
  return [dark, (v) => { applyTheme(v); setDark(v); }];
}

function Header({ route, dark, setDark, total, version }: {
  route: string; dark: boolean; setDark: (v: boolean) => void; total: number; version: string;
}) {
  const link = (href: string, text: string) => (
    <a href={href} style={{ fontSize: 14, fontWeight: route === href.slice(1) ? 600 : 400, color: route === href.slice(1) ? "var(--text)" : "var(--text-muted)" }}>{text}</a>
  );
  return (
    <header style={{ height: 56, display: "flex", alignItems: "center", gap: 20, padding: "0 24px", borderBottom: "1px solid var(--border)", background: "var(--bg)", boxSizing: "border-box", position: "sticky", top: 0, zIndex: 10 }}>
      <a href="#/" style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
        <span style={{ fontSize: 17, fontWeight: 600, color: "var(--text)" }}>drillion</span>
        {total ? <span style={{ fontSize: 13, color: "var(--text-faint)" }}>{total} tasks</span> : null}
        {version ? <span style={{ fontSize: 13, color: "var(--text-faint)" }}>v{version}</span> : null}
      </a>
      <div style={{ flex: 1 }} />
      {link("#/", "Catalogue")}
      {link("#/progress", "Progress")}
      <Toggle checked={dark} onChange={setDark} label={dark ? "Dark" : "Light"} />
    </header>
  );
}

export function App() {
  const route = useHash();
  const [dark, setDark] = useTheme();
  const [head, setHead] = useState({ total: 0, version: "" });
  useSlashToSearch();
  useEffect(() => {
    api<Health>("/health")
      .then((h) => setHead({ total: h.tasks, version: h.version }))
      .catch(() => {});                    // a header without its counts is not worth an error
  }, []);

  // `/task/<slug>` is the task; `/task/<slug>/deps` is its lineage as a screen of its own
  const tail = route.startsWith("/task/") ? route.slice(6) : null;
  const deps = !!tail?.endsWith("/deps");
  const slug = tail ? decodeURIComponent(deps ? tail.slice(0, -"/deps".length) : tail) : null;
  return (
    <>
      <Header route={route} dark={dark} setDark={setDark} {...head} />
      <main style={{ padding: "24px" }}>
        {slug ? (deps ? <Deps key={slug} slug={slug} /> : <Task key={slug} slug={slug} dark={dark} />)
          : route === "/progress" ? <Progress />
          : <Catalogue />}
      </main>
    </>
  );
}
