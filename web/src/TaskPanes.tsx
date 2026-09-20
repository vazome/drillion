import { useEffect, useId, useRef, useState, type PointerEvent, type ReactNode } from "react";
import { DEFAULTS, setPrefs, usePrefs } from "./prefs";
import s from "./TaskPanes.module.css";

/** Keep the brief at least 340px and leave room for the 420px editor and 20px seam. */
export function paneBounds(width: number) {
  const min = Math.min(70, 340 / width * 100);
  return { min, max: Math.max(min, Math.min(70, (width - 440) / width * 100)) };
}

export function TaskPanes({ narrow, children }: { narrow: boolean; children: [ReactNode, ReactNode] }) {
  const { taskPanePercent } = usePrefs();
  const host = useRef<HTMLDivElement>(null);
  const drag = useRef<{ pointer: number; x: number; percent: number } | null>(null);
  const [width, setWidth] = useState(1000);
  const [position, setPosition] = useState<number | null>(null);
  const id = useId();
  const { min, max } = paneBounds(width);
  const saved = Number.isFinite(taskPanePercent) ? taskPanePercent : DEFAULTS.taskPanePercent;
  const clamp = (value: number) => Math.max(min, Math.min(max, value));
  const percent = clamp(position ?? saved);

  useEffect(() => {
    const element = host.current;
    if (!element) return;
    const observer = new ResizeObserver(() => {
      setWidth(element.getBoundingClientRect().width);
      if (narrow) {
        drag.current = null;
        setPosition(null);
      }
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, [narrow]);

  function finish(event: PointerEvent<HTMLDivElement>) {
    if (drag.current?.pointer !== event.pointerId) return;
    drag.current = null;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
    setPosition(null);
    setPrefs({ taskPanePercent: percent });
  }

  return (
    <div ref={host} className={s.root} data-narrow={narrow || undefined}>
      <div id={id} className={s.brief} style={narrow ? undefined : { width: `${percent}%` }}>{children[0]}</div>
      {!narrow ? <div className={s.separator} role="separator" tabIndex={0}
        aria-label="Brief pane width" aria-controls={id} aria-orientation="vertical"
        aria-valuemin={min} aria-valuemax={max} aria-valuenow={percent}
        aria-valuetext={`${Math.round(percent)} percent`}
        data-dragging={position !== null || undefined}
        onPointerDown={(event) => {
          if (!event.isPrimary || event.button !== 0 || drag.current) return;
          event.preventDefault();
          event.currentTarget.focus();
          event.currentTarget.setPointerCapture(event.pointerId);
          drag.current = { pointer: event.pointerId, x: event.clientX, percent };
          setPosition(percent);
        }}
        onPointerMove={(event) => {
          const start = drag.current;
          if (start?.pointer !== event.pointerId) return;
          setPosition(clamp(start.percent + (event.clientX - start.x) / width * 100));
        }}
        onPointerUp={finish} onPointerCancel={finish} onLostPointerCapture={finish}
        onKeyDown={(event) => {
          const next = { ArrowLeft: percent - 2, ArrowRight: percent + 2, Home: min, End: max }[event.key];
          if (next === undefined) return;
          event.preventDefault();
          setPrefs({ taskPanePercent: clamp(next) });
        }} /> : null}
      <div className={s.editor}>{children[1]}</div>
    </div>
  );
}
