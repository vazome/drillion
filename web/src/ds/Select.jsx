import React from "react";
import s from "./Select.module.css";
export function Select({ value, onChange, options = [], placeholder, disabled = false, mono = false, ariaLabel, className, style }) {
  const opts = options.map((o) => (typeof o === "string" ? { value: o, label: o } : o));
  return (
    <span className={s.wrap}>
      <select value={value} disabled={disabled} aria-label={ariaLabel} data-mono={mono ? "" : undefined}
        onChange={onChange ? (e) => onChange(e.target.value) : undefined}
        className={[s.root, className].filter(Boolean).join(" ")} style={style}>
        {placeholder ? <option value="">{placeholder}</option> : null}
        {opts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
      <span aria-hidden="true" className={s.caret}>▾</span>
    </span>
  );
}
