import React from "react";
import s from "./NoteField.module.css";
export function NoteField({ value = "", onChange, label = "Note", hint = "yours, kept with the task", dirty = false, placeholder, rows = 3, ariaLabel, className, style }) {
  return (
    <div data-dirty={dirty ? "" : undefined} className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <div className={s.label}>
        {label}
        <span className={s.hint}> · {dirty ? "unsaved" : hint}</span>
      </div>
      <textarea value={value} rows={rows} placeholder={placeholder} aria-label={ariaLabel || label} className={s.field}
        onChange={onChange ? (e) => onChange(e.target.value) : undefined}></textarea>
    </div>
  );
}
