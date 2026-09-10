import React from "react";
import s from "./Input.module.css";
export function Input({ value, onChange, placeholder, mono = false, ariaLabel, className, style }) {
  return (
    <input value={value} placeholder={placeholder} aria-label={ariaLabel} data-mono={mono ? "" : undefined}
      onChange={onChange ? (e) => onChange(e.target.value) : undefined}
      className={[s.root, className].filter(Boolean).join(" ")} style={style} />
  );
}
