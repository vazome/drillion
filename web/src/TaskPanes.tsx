import { useEffect, useId, useRef, useState, type PointerEvent, type ReactNode } from "react";
import { DEFAULTS, setPrefs, usePrefs } from "./prefs";
import s from "./TaskPanes.module.css";

/** Keep the brief at least 340px and leave room for the 420px editor and 20px seam. */
export function paneBounds(width: number) {
  const min = Math.min(70, 340 / width * 100);
  return { min, max: Math.max(min, Math.min(70, (width - 440) / width * 100)) };
}

/** Keep the output at least 120px and leave the 240px editor, the 60px toolbar and the 8px
 *  splitter above it. */
export function resultBounds(height: number) {
  const min = Math.min(80, 120 / height * 100);
  return { min, max: Math.max(min, Math.min(80, (height - 308) / height * 100)) };
}

/** A pane divider that follows a drag or the arrow keys. `value` is the percent of `span` px
 *  the pane it controls takes, live while dragging: `onDrag` reports each move and `null` when
 *  the drag ends, `onCommit` saves where a drag or a key left it. A `vertical` divider controls
 *  the pane to its left, a `horizontal` one the pane below it. `onReset` answers a double-click
 *  or Enter. */
export function Splitter({ orientation, span, value, min, max, label, controls, title, className, onDrag, onCommit, onReset }: {
  orientation: "vertical" | "horizontal";
  span: number;
  value: number;
  min: number;
  max: number;
  label: string;
  controls: string;
  title?: string;
  className?: string;
  onDrag: (percent: number | null) => void;
  onCommit: (percent: number) => void;
  onReset?: () => void;
}) {
  const drag = useRef<{ pointer: number; at: number; percent: number } | null>(null);
  const [dragging, setDragging] = useState(false);
  const vertical = orientation === "vertical";
  const clamp = (next: number) => Math.max(min, Math.min(max, next));
  const at = (event: PointerEvent) => (vertical ? event.clientX : -event.clientY);

  function finish(event: PointerEvent<HTMLDivElement>) {
    if (drag.current?.pointer !== event.pointerId) return;
    drag.current = null;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
    setDragging(false);
    onDrag(null);
    onCommit(value);
  }

  return (
    <div className={[s.separator, className].filter(Boolean).join(" ")} role="separator" tabIndex={0} title={title}
      aria-label={label} aria-controls={controls} aria-orientation={orientation}
      aria-valuemin={min} aria-valuemax={max} aria-valuenow={value}
      aria-valuetext={`${Math.round(value)} percent`}
      data-dragging={dragging || undefined}
      onPointerDown={(event) => {
        if (!event.isPrimary || event.button !== 0 || drag.current) return;
        event.preventDefault();
        event.currentTarget.focus();
        event.currentTarget.setPointerCapture(event.pointerId);
        drag.current = { pointer: event.pointerId, at: at(event), percent: value };
        setDragging(true);
        onDrag(value);
      }}
      onPointerMove={(event) => {
        const start = drag.current;
        if (start?.pointer !== event.pointerId) return;
        onDrag(clamp(start.percent + (at(event) - start.at) / span * 100));
      }}
      onPointerUp={finish} onPointerCancel={finish} onLostPointerCapture={finish}
      onDoubleClick={onReset}
      onKeyDown={(event) => {
        if (event.key === "Enter" && onReset) {
          event.preventDefault();
          onReset();
          return;
        }
        const keys: Record<string, number> = vertical
          ? { ArrowLeft: value - 2, ArrowRight: value + 2, Home: min, End: max }
          : { ArrowDown: value - 2, ArrowUp: value + 2, Home: min, End: max };
        const next = keys[event.key];
        if (next === undefined) return;
        event.preventDefault();
        onCommit(clamp(next));
      }} />
  );
}

/** `fixed` pins the brief to a width in px, the way Review narrows it; the splitter goes. */
export function TaskPanes({ narrow, fixed, children }: { narrow: boolean; fixed?: number; children: [ReactNode, ReactNode] }) {
  const { taskPanePercent } = usePrefs();
  const host = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(1000);
  const [position, setPosition] = useState<number | null>(null);
  const id = useId();
  const { min, max } = paneBounds(width);
  const saved = Number.isFinite(taskPanePercent) ? taskPanePercent : DEFAULTS.taskPanePercent;
  const percent = Math.max(min, Math.min(max, position ?? saved));

  useEffect(() => {
    const element = host.current;
    if (!element) return;
    const observer = new ResizeObserver(() => {
      setWidth(element.getBoundingClientRect().width);
      if (narrow) setPosition(null);
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, [narrow]);

  return (
    <div ref={host} className={s.root} data-narrow={narrow || undefined}>
      <div id={id} className={s.brief} style={narrow ? undefined : fixed ? { width: fixed, minWidth: 0 } : { width: `${percent}%` }}>{children[0]}</div>
      {!narrow && !fixed ? <Splitter orientation="vertical" span={width} value={percent} min={min} max={max}
        label="Brief pane width" controls={id}
        onDrag={setPosition} onCommit={(next) => setPrefs({ taskPanePercent: next })} /> : null}
      {!narrow && fixed ? <div className={s.seam} /> : null}
      <div className={s.editor}>{children[1]}</div>
    </div>
  );
}
