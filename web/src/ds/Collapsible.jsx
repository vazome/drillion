import React from "react";
import s from "./Collapsible.module.css";
export function Collapsible({ label, meta, open, defaultOpen = false, onToggle, disabled = false, mono = true, children, className, style }) {
  const [inner, setInner] = React.useState(defaultOpen);
  const isOpen = open === undefined ? inner : open;
  const toggle = () => { if (disabled) return; if (open === undefined) setInner(!isOpen); if (onToggle) onToggle(!isOpen); };
  return (
    <div className={className} style={style}>
      <button type="button" aria-expanded={isOpen} disabled={disabled} onClick={toggle} className={s.head}>
        <span aria-hidden="true" className={s.caret} data-open={isOpen ? "" : undefined}>▸</span>
        <span className={s.title}>{label}</span>
        {meta ? <span className={s.meta}>{meta}</span> : null}
      </button>
      {isOpen ? <div className={s.body + " m-expand"} data-prose={mono ? undefined : ""}>{children}</div> : null}
    </div>
  );
}
