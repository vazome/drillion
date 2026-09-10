import React from "react";
import s from "./Tip.module.css";
/* Hover bubble shared by the chart cards. Dark bubble, centred on `x`, clamped inside the card.
   `y` is the top of the hovered cell; omit it and the bubble sits at the top of the plot area. */
export function Tip({ text, x, y, className, style }) {
  /* Keep the bubble inside the card: clamp its centre once it has measured itself. */
  const clamp = (el) => {
    if (!el) return;
    const w = el.offsetWidth / 2 + 2;
    const room = (el.offsetParent || el.parentElement).clientWidth;
    el.style.left = Math.min(Math.max(x, w), Math.max(w, room - w)) + "px";
  };
  return (
    <div ref={clamp} className={[s.root, className].filter(Boolean).join(" ")} style={{ left: x, top: y == null ? -6 : y - 8, ...style }}>{text}</div>
  );
}
