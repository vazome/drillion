import { lazy, Suspense, useEffect, useState, type ReactNode } from "react";
import { Dialog, EmptyState } from "./ds/index.js";
import { api, type Health } from "./api";
import { Catalogue } from "./Catalogue";
import { Progress } from "./Progress";
import { Deps } from "./Deps";
import { Settings } from "./Settings";
import { Sidebar, TopBar, type Head } from "./Shell";
import s from "./Shell.module.css";

// the editor bundle is most of the app, and only the task screen needs it
const Task = lazy(() => import("./Task").then((m) => ({ default: m.Task })));

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

/** `#/settings` stays a link anyone can keep, though Settings is no longer a screen of its
 *  own: it opens the dialog, over the catalogue, since a link arrives with no screen to be
 *  over. The sidebar and the top bar open the same dialog without touching the route at all, which is what
 *  keeps the task you had open underneath it. */
const SETTINGS = "#/settings";

export function App() {
  const route = useHash();
  const [dark, setDark] = useTheme();
  const [head, setHead] = useState<Head>({ total: 0, version: "", python: "" });
  const [settings, setSettings] = useState(location.hash === SETTINGS);
  useSlashToSearch();
  // any navigation closes it, and the link opens it: a modal that outlives the screen it
  // was opened over is a door with no way out of it
  useEffect(() => {
    const on = () => setSettings(location.hash === SETTINGS);
    addEventListener("hashchange", on);
    return () => removeEventListener("hashchange", on);
  }, []);
  const closeSettings = () => {
    setSettings(false);
    if (location.hash === SETTINGS) location.replace("#/");  // the deep link, spent
  };
  useEffect(() => {
    api<Health>("/health")
      .then((h) => setHead({ total: h.tasks, version: h.version, python: h.python }))
      .catch(() => {});                    // a header without its counts is not worth an error
  }, []);

  // `/task/<slug>` is the task; `/task/<slug>/deps` is its lineage as a screen of its own
  const tail = route.startsWith("/task/") ? route.slice(6) : null;
  const deps = !!tail?.endsWith("/deps");
  const slug = tail ? decodeURIComponent(deps ? tail.slice(0, -"/deps".length) : tail) : null;
  const chrome = { route, dark, setDark, onSettings: () => setSettings(true) };
  const bar = (crumbs: ReactNode) => <TopBar {...chrome} crumbs={crumbs} />;
  return (
    <div className={s.app} data-layout={slug && !deps ? "bar" : undefined}>
      {slug && !deps ? (
        <Suspense fallback={<>{bar(null)}<EmptyState message="Loading…" /></>}>
          <Task key={slug} slug={slug} dark={dark} bar={bar} />
        </Suspense>
      ) : <>
        <Sidebar {...chrome} head={head} />
        <TopBar {...chrome} className={s.narrow} />
        <main className={s.main}>
          {slug ? <Deps key={slug} slug={slug} /> : route === "/progress" ? <Progress /> : <Catalogue />}
        </main>
      </>}
      <Dialog open={settings} onClose={closeSettings} label="Settings">
        <Settings />
      </Dialog>
    </div>
  );
}
