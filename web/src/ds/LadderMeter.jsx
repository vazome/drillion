import React from "react";
export function LadderMeter({ box = 0, intervals = [2, 4, 8, 16, 28, 60, 120], style }) {
  const title = box > 0 ? "box " + box + " of " + intervals.length + " — every " + intervals[box - 1] + " days" : "not on the ladder yet";
  return (
    <span title={title} style={{ display: "inline-flex", gap: "2px", ...style }}>
      {intervals.map((_, i) => (
        <i key={i} style={{ width: "7px", height: "11px", borderRadius: "2px", display: "block", background: i < box ? "var(--accent)" : "var(--border)" }}></i>
      ))}
    </span>
  );
}
