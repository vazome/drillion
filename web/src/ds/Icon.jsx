import React from "react";
import { ICONS } from "./icons.js";
import s from "./Icon.module.css";

/** One icon from drillion's fixed list — 32 from IBM Carbon, in icons.js. It always sits
 *  beside a word, so it is hidden from assistive tech and the word carries the meaning; it
 *  takes the colour of the text around it and never carries a state on its own. An icon-only
 *  control (Dismiss) names itself with aria-label on the button, never on the icon.
 *  16px beside 13–15px text, 14px beside 12px labels, 12px in the smallest marks. */
export function Icon({ name, size = 16, className, style }) {
  const icon = ICONS[name];
  if (!icon) return null;
  return (
    <svg viewBox={icon.viewBox} width={size} height={size} fill="currentColor"
      aria-hidden="true" focusable="false"
      className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      {icon.nodes.map(([tag, attrs], i) => React.createElement(tag, { key: i, ...attrs }))}
    </svg>
  );
}
