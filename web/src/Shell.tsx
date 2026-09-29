import { useEffect, useState, type ReactNode } from "react";
import { Icon, TagChip } from "./ds/index.js";
import { api, FOCUS_SAVED, setFocus, type Picks } from "./api";
import { topicNo } from "./format";
import s from "./Shell.module.css";

/** The tracks that ship a mark in web/public/tracks/; any other wears its first letter. */
const MARKS = new Set(["python", "kubernetes", "helm", "docker", "sql", "git", "argocd", "github-actions"]);
export const trackIcon = (name: string) => (MARKS.has(name) ? `tracks/${name}.svg` : undefined);

/** The wordmark of docs/images/drillion-github-banner-*.svg, cropped: the name takes the
 * accent and the underscore the control edge, so it follows the theme like the favicon does. */
const WORDMARK = "M446.92 199.96H446.22Q443.84 206.4 438.45 210.04Q433.06 213.68 425.78 213.68Q411.92 213.68 404.36 203.67Q396.8 193.66 396.8 175.6Q396.8 157.54 404.36 147.53Q411.92 137.52 425.78 137.52Q433.06 137.52 438.45 141.09Q443.84 144.66 446.22 151.24H446.92V108.4H462.18V212H446.92ZM430.4 200.52Q437.4 200.52 442.16 197.09Q446.92 193.66 446.92 188.06V163.14Q446.92 157.54 442.16 154.11Q437.4 150.68 430.4 150.68Q422.42 150.68 417.66 155.79Q412.9 160.9 412.9 169.3V181.9Q412.9 190.3 417.66 195.41Q422.42 200.52 430.4 200.52ZM484.02 212V139.2H499.28V153.2H499.98Q501.52 147.6 506.42 143.4Q511.32 139.2 520 139.2H524.06V153.9H518.04Q508.94 153.9 504.11 156.84Q499.28 159.78 499.28 165.52V212ZM545.34 126.18Q540.58 126.18 538.41 123.94Q536.24 121.7 536.24 118.2V115.82Q536.24 112.32 538.41 110.08Q540.58 107.84 545.34 107.84Q550.1 107.84 552.2 110.08Q554.3 112.32 554.3 115.82V118.2Q554.3 121.7 552.2 123.94Q550.1 126.18 545.34 126.18ZM537.64 139.2H552.9V212H537.64ZM590.28 212Q582.44 212 578.59 208.01Q574.74 204.02 574.74 196.88V108.4H590V199.54H600.08V212ZM629.34 212Q621.5 212 617.65 208.01Q613.8 204.02 613.8 196.88V108.4H629.06V199.54H639.14V212ZM661.4 126.18Q656.64 126.18 654.47 123.94Q652.3 121.7 652.3 118.2V115.82Q652.3 112.32 654.47 110.08Q656.64 107.84 661.4 107.84Q666.16 107.84 668.26 110.08Q670.36 112.32 670.36 115.82V118.2Q670.36 121.7 668.26 123.94Q666.16 126.18 661.4 126.18ZM653.7 139.2H668.96V212H653.7ZM719.36 213.68Q711.8 213.68 705.57 211.02Q699.34 208.36 695 203.39Q690.66 198.42 688.28 191.35Q685.9 184.28 685.9 175.6Q685.9 166.92 688.28 159.85Q690.66 152.78 695 147.81Q699.34 142.84 705.57 140.18Q711.8 137.52 719.36 137.52Q726.92 137.52 733.15 140.18Q739.38 142.84 743.72 147.81Q748.06 152.78 750.44 159.85Q752.82 166.92 752.82 175.6Q752.82 184.28 750.44 191.35Q748.06 198.42 743.72 203.39Q739.38 208.36 733.15 211.02Q726.92 213.68 719.36 213.68ZM719.36 201.08Q727.2 201.08 731.96 196.25Q736.72 191.42 736.72 181.76V169.44Q736.72 159.78 731.96 154.95Q727.2 150.12 719.36 150.12Q711.52 150.12 706.76 154.95Q702 159.78 702 169.44V181.76Q702 191.42 706.76 196.25Q711.52 201.08 719.36 201.08ZM769.76 212V139.2H785.02V151.24H785.72Q788.1 145.36 792.93 141.44Q797.76 137.52 806.16 137.52Q817.36 137.52 823.59 144.87Q829.82 152.22 829.82 165.8V212H814.56V167.76Q814.56 150.68 800.84 150.68Q797.9 150.68 795.03 151.45Q792.16 152.22 789.92 153.76Q787.68 155.3 786.35 157.68Q785.02 160.06 785.02 163.28V212Z";
function Wordmark({ height }: { height: number }) {
  return (
    <svg viewBox="396 107 494 107" width={height * 494 / 107} height={height} role="img" aria-label="drillion" className={s.wordmark}>
      <path fill="var(--accent)" d={WORDMARK} />
      <rect x="851.22" y="197.54" width="38.56" height="14.46" fill="var(--control-edge)" />
    </svg>
  );
}

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
  // the track just clicked, lit at once while the server saves it; undefined once it has
  const [asked, setAsked] = useState<string | null | undefined>(undefined);
  useEffect(() => {
    const load = () => { api<Picks>("/picks").then((p) => { setPicks(p); setAsked(undefined); }).catch(() => {}); };
    load();
    addEventListener(FOCUS_SAVED, load);
    return () => removeEventListener(FOCUS_SAVED, load);
  }, []);
  const focus = picks?.focus ?? null;
  const pick = (tag: string | null) => {
    setError(null);
    setAsked(tag);
    setFocus(tag).catch((e) => { setAsked(undefined); setError(`Focus is still “${focus ?? "every track"}”: ${e.message}`); });
  };
  const rows = [{ key: null, name: "All tracks", size: head.total },
    ...Object.entries(picks?.tracks ?? {}).map(([name, size]) => ({ key: name, name, size }))];
  const stuck = picks?.stuck;

  return (
    <aside className={s.side}>
      <a href="#/" className={s.brand}><Wordmark height={20} /></a>
      <nav aria-label="Main" className={s.stack}>
        <Nav href="#/" route={route}>Catalogue</Nav>
        <Nav href="#/progress" route={route}>Progress</Nav>
      </nav>
      {picks ? (
        <section aria-labelledby="picks-from" className={s.picks}>
          <h2 id="picks-from" className={s.label}>New picks from</h2>
          <div role="group" aria-labelledby="picks-from" className={s.stack}>
            {rows.map(({ key, name, size }) => {
              const on = (asked === undefined ? focus : asked) === key;
              const icon = key ? trackIcon(key) : undefined;
              return (
                <button key={name} type="button" aria-pressed={on} data-on={on || undefined} onClick={() => pick(key)} className={s.track}>
                  <span className={s.trackHead}>
                    {icon ? <img src={icon} alt="" width={28} height={28} className={s.mark} data-image="" />
                      : <span aria-hidden="true" className={s.mark} data-all={key ? undefined : ""}>
                          {key ? key.charAt(0) : <><i /><i /><i /><i /></>}
                        </span>}
                    <span className={s.trackName}>{name}</span>
                    <span className={s.count}>{size}</span>
                  </span>
                  <span aria-hidden="true" className={s.size} style={{ width: `${head.total ? (100 * size) / head.total : 0}%` }} />
                </button>
              );
            })}
          </div>
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
      <a href="#/" className={s.barBrand}><Wordmark height={18} /></a>
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
