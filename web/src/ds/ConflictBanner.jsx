import React from "react";
import s from "./ConflictBanner.module.css";
function Action({ label, onClick, strong, disabled }) {
  return (
    <button type="button" disabled={disabled} onClick={onClick} className={s.action} data-strong={strong ? "" : undefined}>{label}</button>
  );
}
export function ConflictBanner({ message = "This task changed on disk.", detail, reloadLabel = "Reload from disk", keepLabel = "Keep mine", onReload, onKeep, disabled = false, className, style }) {
  return (
    <div role="alert" className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <div className={s.text}>
        <span className={s.message}>{message}</span>
        {detail ? <span className={s.detail}>{detail}</span> : null}
      </div>
      <Action label={reloadLabel} onClick={onReload} disabled={disabled} strong />
      <Action label={keepLabel} onClick={onKeep} disabled={disabled} />
    </div>
  );
}
