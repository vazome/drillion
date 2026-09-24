import { useEffect, useState, type ReactNode } from "react";
import { Icon, TagChip } from "./ds/index.js";
import { api, FOCUS_SAVED, setFocus, type Picks } from "./api";
import { topicNo } from "./format";
import s from "./Shell.module.css";

/** The tracks that ship a mark in web/public/tracks/; any other wears its first letter. */
const MARKS = new Set(["python", "kubernetes", "helm", "docker"]);
export const trackIcon = (name: string) => (MARKS.has(name) ? `tracks/${name}.svg` : undefined);

export interface Head { total: number; version: string; python: string }
interface Chrome { dark: boolean; setDark: (v: boolean) => void; onSettings: () => void }

/** The theme as a word beside its icon; the sidebar draws a switch after it. */
function Theme({ dark, setDark, track = false }: Pick<Chrome, "dark" | "setDark"> & { track?: boolean }) {
  return (
    <button type="button" role="switch" aria-checked={dark} onClick={() => setDark(!dark)} className={s.item}>
      <Icon name={dark ? "Asleep" : "Sun"} />
      <span className={s.grow}>{dark ? "Dark" : "Light"}</span>
      {track ? <span aria-hidden="true" className={s.switch} data-on={dark || undefined}><span /></span> : null}
    </button>
  );
}

const Nav = ({ href, route, children }: { href: string; route: string; children: ReactNode }) => {
  // every screen but Progress sits under the catalogue, lineage included
  const here = href === "#/progress" ? route === "/progress" : route !== "/progress";
  return <a href={href} aria-current={here ? "page" : undefined} className={s.nav}>{children}</a>;
};

/** The shell every screen but the task page sits in: where to go, what new picks come
 *  from, and at the foot the things that are not screens. */
export function Sidebar({ route, head, dark, setDark, onSettings }: Chrome & { route: string; head: Head }) {
  const [picks, setPicks] = useState<Picks | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const load = () => { api<Picks>("/picks").then(setPicks).catch(() => {}); };
    load();
    addEventListener(FOCUS_SAVED, load);
    return () => removeEventListener(FOCUS_SAVED, load);
  }, []);
  const focus = picks?.focus ?? null;
  const pick = (tag: string | null) => {
    setError(null);
    setFocus(tag).catch((e) => setError(`Focus is still “${focus ?? "every track"}”: ${e.message}`));
  };
  const rows = [{ key: null, name: "All tracks", size: head.total },
    ...Object.entries(picks?.tracks ?? {}).map(([name, size]) => ({ key: name, name, size }))];
  const stuck = picks?.stuck;

  return (
    <aside className={s.side}>
      <a href="#/" className={s.brand}>drillion{head.total ? <span className={s.count}>{head.total} tasks</span> : null}</a>
      <nav aria-label="Main" className={s.stack}>
        <Nav href="#/" route={route}>Catalogue</Nav>
        <Nav href="#/progress" route={route}>Progress</Nav>
      </nav>
      {picks ? (
        <section aria-labelledby="picks-from" className={s.picks}>
          <h2 id="picks-from" className={s.label}>New picks from</h2>
          <div role="group" aria-labelledby="picks-from" className={s.stack}>
            {rows.map(({ key, name, size }) => {
              const on = focus === key;
              const icon = key ? trackIcon(key) : undefined;
              return (
                <button key={name} type="button" aria-pressed={on} data-on={on || undefined} onClick={() => pick(key)} className={s.track}>
                  <span className={s.trackHead}>
                    {icon ? <img src={icon} alt="" width={22} height={22} className={s.mark} data-image="" />
                      : <span aria-hidden="true" className={s.mark} data-all={key ? undefined : ""}>
                          {key ? key.charAt(0) : <><i /><i /><i /><i /></>}
                        </span>}
                    <span className={s.trackName}>{name}</span>
                    <span className={s.count}>{size}</span>
                  </span>
                  <span aria-hidden="true" className={s.size} style={{ width: `calc((100% - 32px) * ${head.total ? size / head.total : 0})` }} />
                </button>
              );
            })}
          </div>
          <p className={s.note}>Reviews still come from every track.</p>
          {stuck ? (
            <p className={s.note}>
              You keep struggling with <TagChip label={stuck.tag} small active={focus === stuck.tag}
                onClick={() => pick(focus === stuck.tag ? null : stuck.tag)} /> · {stuck.flagged} flagged
            </p>
          ) : null}
          {error ? <p role="alert" className={s.note} data-error="">{error}</p> : null}
        </section>
      ) : null}
      <div className={s.foot}>
        <button type="button" onClick={onSettings} className={s.item}><Icon name="Settings" />Settings</button>
        <Theme dark={dark} setDark={setDark} track />
        {head.version ? <span className={s.version}>v{head.version}{head.python ? ` · Python ${head.python}` : ""}</span> : null}
      </div>
    </aside>
  );
}

/** The 48px bar: the task page's whole chrome, and every other screen's below 1100px. */
export function TopBar({ route, crumbs, dark, setDark, onSettings, className }: Chrome & {
  route: string; crumbs?: ReactNode; className?: string;
}) {
  return (
    <header className={[s.bar, className].filter(Boolean).join(" ")}>
      <a href="#/" className={s.barBrand}>drillion</a>
      {crumbs ? <nav aria-label="Breadcrumb" className={s.crumbs}>{crumbs}</nav> : null}
      <span className={s.grow} />
      <nav aria-label="Main" className={s.barNav}>
        {crumbs ? null : <Nav href="#/" route={route}>Catalogue</Nav>}
        <Nav href="#/progress" route={route}>Progress</Nav>
        <button type="button" onClick={onSettings} className={s.item}><Icon name="Settings" />Settings</button>
        <Theme dark={dark} setDark={setDark} />
      </nav>
    </header>
  );
}

/** `← Catalogue / docker / 289`: where a task sits, for the task page's bar. */
export const Crumbs = ({ group, topic }: { group?: string; topic: number }) => (
  <>
    <a href="#/"><Icon name="ArrowLeft" size={14} />Catalogue</a>
    {group ? <><span aria-hidden="true">/</span><span>{group}</span></> : null}
    <span aria-hidden="true">/</span><span className={s.crumbNo}>{topicNo(topic)}</span>
  </>
);
