import React from "react";
import s from "./Toggle.module.css";
export function Toggle({ checked = false, onChange, label, disabled = false, ariaLabel, className, style }) {
  const on = checked && !disabled;
  return (
    <button type="button" role="switch" aria-checked={!!checked} aria-label={label ? undefined : ariaLabel} disabled={disabled}
      data-on={on ? "" : undefined} data-checked={checked ? "" : undefined}
      onClick={onChange ? () => onChange(!checked) : undefined}
      className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <span aria-hidden="true" className={s.track}><span className={s.knob}></span></span>
      {label ? <span className={s.label}>{label}</span> : null}
    </button>
  );
}
