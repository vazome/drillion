/** The preferences that describe the person rather than their practice: which keys the
 *  editor answers to, how it is set, and whether the timer is on screen. They live in this
 *  browser beside the theme, so they are not in a backup and not in anyone's progress.
 *
 *  A component reads them with `usePrefs()` and writes with `setPrefs()`; the store is
 *  shared, so Settings changing a value reaches an editor already on screen. */
import { useSyncExternalStore } from "react";

const KEY = "drillion-prefs";
const OLD = "drillion-editor-mode"; // the Vim switch these grew out of

export type Prefs = {
  keys: "regular" | "vim" | "emacs";
  font: "shipped" | "jetbrains" | "fira" | "cascadia" | "source" | "plex" | "inconsolata" | "system";
  fontSize: number;
  ligatures: boolean;
  tabSize: number;
  wordWrap: boolean;
  relativeLines: boolean;
  showTimer: boolean;
};

/** Every default is what drillion did before there was a setting, so a first visit after an
 *  upgrade looks exactly like the last one before it. */
export const DEFAULTS: Prefs = {
  keys: "regular",
  font: "shipped",
  fontSize: 14,
  ligatures: false,
  tabSize: 4,
  wordWrap: true,
  relativeLines: false,
  showTimer: true,
};

/** Only what a self-hosted install already has on disk: the faces drillion ships, and
 *  whatever the machine calls monospace. Nothing is fetched from anyone. The first three
 *  after the default carry programming ligatures, which the ligature setting turns on. */
export const FONTS: { value: Prefs["font"]; label: string; stack: string }[] = [
  { value: "shipped", label: "Spline Sans Mono", stack: '"Spline Sans Mono", ui-monospace, monospace' },
  { value: "jetbrains", label: "JetBrains Mono", stack: '"JetBrains Mono", ui-monospace, monospace' },
  { value: "fira", label: "Fira Code", stack: '"Fira Code", ui-monospace, monospace' },
  { value: "cascadia", label: "Cascadia Code", stack: '"Cascadia Code", ui-monospace, monospace' },
  { value: "source", label: "Source Code Pro", stack: '"Source Code Pro", ui-monospace, monospace' },
  { value: "plex", label: "IBM Plex Mono", stack: '"IBM Plex Mono", ui-monospace, monospace' },
  { value: "inconsolata", label: "Inconsolata", stack: '"Inconsolata", ui-monospace, monospace' },
  { value: "system", label: "System monospace", stack: "ui-monospace, Consolas, Menlo, monospace" },
];

export const fontStack = (font: Prefs["font"]) =>
  (FONTS.find((f) => f.value === font) ?? FONTS[0]).stack;

function load(): Prefs {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { ...DEFAULTS, ...(JSON.parse(raw) as Partial<Prefs>) };
    // the one-setting era: a Vim user keeps their keys without being asked again
    return { ...DEFAULTS, keys: localStorage.getItem(OLD) === "vim" ? "vim" : "regular" };
  } catch {
    return DEFAULTS;
  }
}

let cache = load();
const listeners = new Set<() => void>();
const announce = () => listeners.forEach((l) => l());

addEventListener("storage", (e) => {
  if (e.key !== KEY) return; // another tab of the same drillion, changed in its Settings
  cache = load();
  announce();
});

export function setPrefs(patch: Partial<Prefs>) {
  cache = { ...cache, ...patch };
  localStorage.setItem(KEY, JSON.stringify(cache));
  announce();
}

export function usePrefs(): Prefs {
  return useSyncExternalStore(
    (l) => { listeners.add(l); return () => listeners.delete(l); },
    () => cache,
  );
}
