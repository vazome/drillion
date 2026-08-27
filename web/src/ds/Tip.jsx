import React from "react";
/* Hover bubble shared by the chart cards. Dark bubble, centred on `x`, clamped inside the card.
   `y` is the top of the hovered cell; omit it and the bubble sits at the top of the plot area. */
export function Tip({ text, x, y }) {
  /* Keep the bubble inside the card: clamp its centre once it has measured itself. */
  const clamp = (el) => {
    if (!el) return;
    const w = el.offsetWidth / 2 + 2;
    const room = (el.offsetParent || el.parentElement).clientWidth;
    el.style.left = Math.min(Math.max(x, w), Math.max(w, room - w)) + "px";
  };
  return (
    <div ref={clamp} style={{ position: "absolute", left: x, top: y == null ? -6 : y - 8, transform: "translate(-50%, -100%)", pointerEvents: "none", zIndex: 2, whiteSpace: "nowrap", fontSize: 12.5, padding: "5px 9px", borderRadius: "var(--radius-sm)", background: "var(--text)", color: "var(--bg)", boxShadow: "0 2px 8px rgba(0,0,0,.18)" }}>{text}</div>
  );
}
