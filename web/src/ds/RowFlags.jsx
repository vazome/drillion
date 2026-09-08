import React from "react";
const numFlag = (n) => "#" + String(n).padStart(3, "0");
const asRef = (t) => (typeof t === "object" ? t : { topic: t });
export function RowFlags({ needs = [], onNeedsClick, lapses = 0, lapseLimit = 0, style }) {
  const marks = [];
  if (needs.length) {
    const refs = needs.map(asRef);
    const label = "needs " + refs.map((r) => numFlag(r.topic)).join(" ");
    const why = "Not offered as a new pick until these are passed: " + refs.map((r) => numFlag(r.topic) + (r.title ? " " + r.title : "")).join(", ");
    marks.push(onNeedsClick
      ? <button key="needs" type="button" title={why + " — opens the lineage"} onClick={(e) => { e.preventDefault(); e.stopPropagation(); onNeedsClick(e); }}
          style={{ background: "transparent", border: "none", padding: 0, font: "inherit", color: "inherit", cursor: "pointer", textDecoration: "underline", textDecorationStyle: "dotted", textUnderlineOffset: "2px" }}>{label}</button>
      : <span key="needs" title={why}>{label}</span>);
  }
  if (lapseLimit && lapses >= lapseLimit) {
    marks.push(
      <span key="lapses" title={"You have struggled with this " + lapses + " times; the hints or the prereqs may be the problem, not you."}>
        struggled {lapses}×
      </span>
    );
  }
  if (!marks.length) return null;
  return <span style={{ display: "inline-flex", gap: "10px", fontSize: "12.5px", color: "var(--text-faint)", whiteSpace: "nowrap", ...style }}>{marks}</span>;
}
