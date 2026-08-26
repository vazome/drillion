import { useCallback, useEffect, useState } from "react";
import { Select, Toggle } from "./ds/index.js";
import { post } from "./api";
import { Catalogue } from "./Catalogue";
import { Exercise } from "./Exercise";
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

function Header({ route, dark, setDark, focus, tags, total, daysLeft, onFocus }: {
  route: string; dark: boolean; setDark: (v: boolean) => void;
  focus: string | null; tags: string[]; total: number; daysLeft: number;
  onFocus: (tag: string) => void;
}) {
  const link = (href: string, text: string) => (
    <a href={href} style={{ fontSize: 14, fontWeight: route === href.slice(1) ? 600 : 400, color: route === href.slice(1) ? "var(--text)" : "var(--text-muted)" }}>{text}</a>
  );
  return (
    <header style={{ height: 56, display: "flex", alignItems: "center", gap: 20, padding: "0 24px", borderBottom: "1px solid var(--border)", background: "var(--bg)", boxSizing: "border-box", position: "sticky", top: 0, zIndex: 10 }}>
      <a href="#/" style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
        <span style={{ fontSize: 17, fontWeight: 600, color: "var(--text)" }}>drillion</span>
        {total ? <span style={{ fontSize: 13, color: "var(--text-faint)" }}>{total} drills</span> : null}
      </a>
      <div style={{ flex: 1 }} />
      <label style={{ fontSize: 13, color: "var(--text-muted)", display: "flex", gap: 6, alignItems: "center" }}>
        Focus:
        <Select value={focus ?? ""} onChange={onFocus} options={tags} placeholder="no focus" ariaLabel="Focus tag" style={{ height: 30, fontSize: 13 }} />
      </label>
      {link("#/", "Catalogue")}
      {link("#/progress", "Progress")}
      {daysLeft ? <span className="tabular" style={{ fontSize: 13, color: "var(--text-faint)", fontFamily: "var(--font-mono)" }}>{daysLeft} days left</span> : null}
      <Toggle checked={dark} onChange={setDark} label={dark ? "Dark" : "Light"} />
    </header>
  );
}

export function App() {
  const route = useHash();
  const [dark, setDark] = useTheme();
  // The header's focus/tags/total live on the catalogue payload; one shared copy, refetched on nav.
  const [head, setHead] = useState({ focus: null as string | null, tags: [] as string[], total: 0, daysLeft: 0 });
  const onHead = useCallback((h: typeof head) => setHead(h), []);
  const setFocus = (tag: string) => {
    setHead((h) => ({ ...h, focus: tag || null }));
    post("/focus", { tag: tag || null }).catch(() => {});
  };

  const slug = route.startsWith("/ex/") ? decodeURIComponent(route.slice(4)) : null;
  return (
    <>
      <Header route={route} dark={dark} setDark={setDark} onFocus={setFocus} {...head} />
      <main style={{ padding: "24px" }}>
        {slug ? <Exercise slug={slug} dark={dark} />
          : route === "/progress" ? <Progress />
          : <Catalogue onHead={onHead} focus={head.focus} />}
      </main>
    </>
  );
}
