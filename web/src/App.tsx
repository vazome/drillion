import { useEffect, useState } from "react";
import { Toggle } from "./ds/index.js";
import { api, type Health } from "./api";
import { Catalogue } from "./Catalogue";
import { Task } from "./Task";
import { Progress } from "./Progress";

/** Hash routing, whole implementation. Three routes do not need a router. */
export function useHash() {
  const [hash, setHash] = useState(() => location.hash.slice(1) || "/");
  useEffect(() => {
    const on = () => setHash(location.hash.slice(1) || "/");
    addEventListener("hashchange", on);
    return () => removeEventListener("hashchange", on);
  }, []);
  return hash;
}

/** Applied before first render and inside the setter, so `.dark` is never a frame behind —
 * the editor reads its colours straight off these variables with getComputedStyle. */
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
  // Both numbers ride on /api/health — the one endpoint that reports the version, and the
  // cheapest place to ask how many tasks there are. The header fetches them itself because
  // it renders on every route, including a deep link to #/progress or a task.
  const [head, setHead] = useState({ total: 0, version: "" });
  useEffect(() => {
    api<Health>("/health")
      .then((h) => setHead({ total: h.tasks, version: h.version }))
      .catch(() => {});                    // a header without its counts is not worth an error
  }, []);

  const slug = route.startsWith("/task/") ? decodeURIComponent(route.slice(6)) : null;
  return (
    <>
      <Header route={route} dark={dark} setDark={setDark} {...head} />
      <main style={{ padding: "24px" }}>
        {slug ? <Task slug={slug} dark={dark} />
          : route === "/progress" ? <Progress />
          : <Catalogue />}
      </main>
    </>
  );
}
