import { useSyncExternalStore } from "react";

/** Below this every screen falls back to one column: the bar replaces the sidebar, panes
 *  stack and graphs lose their curves. Desktop at 1280px and up is still the design. */
const NARROW = "(max-width: 1099px)";
const watch = (onChange: () => void) => {
  const q = matchMedia(NARROW);
  q.addEventListener("change", onChange);
  return () => q.removeEventListener("change", onChange);
};
const now = () => matchMedia(NARROW).matches;

export const useNarrow = () => useSyncExternalStore(watch, now);
