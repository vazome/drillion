import React from "react";
import s from "./Dialog.module.css";
import { Button } from "./Button.jsx";

/** A modal panel over the current screen. It is a native <dialog> opened with showModal(),
 *  which is where the focus trap, the Escape key, the inert background and the backdrop all
 *  come from — none of them are ours to get wrong. Clicking the backdrop closes it too. */
export function Dialog({ open = false, onClose, label, children, className, style }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    else if (!open && el.open) el.close();
  }, [open]);

  return (
    <dialog ref={ref} aria-label={label} onClose={() => onClose?.()}
      onClick={(e) => { if (e.target === ref.current) ref.current.close(); }}
      className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <div className={s.head}>
        <h2 className={s.title}>{label}</h2>
        <div className={s.spacer}></div>
        <Button variant="quiet" onClick={() => ref.current?.close()}>Close</Button>
      </div>
      <div className={s.body}>{children}</div>
    </dialog>
  );
}
