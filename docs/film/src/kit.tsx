import type { CSSProperties, ReactNode } from "react";
import { loadFont } from "@remotion/fonts";
import { AbsoluteFill, Easing, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
// the app's tokens, minus fonts.css, whose absolute /fonts urls the film serves differently
import "@ds/tokens/colors.css";
import "@ds/tokens/typography.css";
import "@ds/tokens/spacing.css";
import "@ds/tokens/base.css";
import "./aliases.css";

loadFont({ family: "IBM Plex Sans", url: staticFile("fonts/ibm-plex-sans-latin.woff2"), weight: "400 600" });
loadFont({ family: "IBM Plex Sans", url: staticFile("fonts/ibm-plex-sans-latin-italic.woff2"), style: "italic" });
loadFont({ family: "Spline Sans Mono", url: staticFile("fonts/spline-sans-mono-latin.woff2"), weight: "400 600" });

/** The motion tokens, as easings a frame can be run through. */
export const OUT = Easing.bezier(0.16, 0.84, 0.44, 1);
export const INOUT = Easing.bezier(0.65, 0, 0.35, 1);

/** 0 → 1 across `dur` frames from `start`, eased; held at either end. */
export function useT(start: number, dur: number, easing = OUT) {
  const f = useCurrentFrame();
  return interpolate(f, [start, start + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing });
}

/** A spring from `start`: 0 → 1 with the given bounce, 0 before it starts. */
export function useSpring(start: number, damping = 200, durationInFrames?: number) {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: f - start, fps, config: { damping }, durationInFrames });
}

export const mix = (t: number, a: number, b: number) => a + (b - a) * t;

/** Something arriving: rises `y` px while it fades in. */
export function rise(t: number, y = 18): CSSProperties {
  return { opacity: t, transform: `translateY(${mix(t, y, 0)}px)` };
}

/** The dark desk every scene sits on. `light` is how the end card turns the theme over. */
export function Stage({ children, light = false, style }: { children: ReactNode; light?: boolean; style?: CSSProperties }) {
  return (
    <AbsoluteFill className={light ? undefined : "dark"}
      style={{ background: "var(--bg)", color: "var(--text)", fontFamily: "var(--font-sans)", ...style }}>
      {children}
    </AbsoluteFill>
  );
}

/** The line above a shot: a mono eyebrow in the scene's colour, then the sentence. */
export function Caption({ eyebrow, color = "var(--accent)", children, at = 4, left = 96, top = 64, inline = false, size = 56 }: {
  eyebrow: string; color?: string; children: ReactNode; at?: number; left?: number; top?: number; inline?: boolean; size?: number;
}) {
  const a = useT(at, 16);
  const b = useT(at + 5, 20);
  return (
    <div style={{ position: "absolute", left, top, display: "flex", flexDirection: inline ? "row" : "column", alignItems: inline ? "baseline" : "flex-start", gap: inline ? 24 : 14 }}>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 18, letterSpacing: "0.08em", color, ...rise(a, 10) }}>{eyebrow}</span>
      <h1 style={{ margin: 0, fontSize: size, lineHeight: 1.08, fontWeight: 500, letterSpacing: "-0.02em", ...rise(b, 22) }}>{children}</h1>
    </div>
  );
}

export type Shot = { scale: number; x: number; y: number };

/** The app, in a window the camera looks through: `shot` places a 1600-wide app inside it
 *  (scale, then the app point at the window's top left). Pass a moving shot for a push-in. */
export function Window({ left, top, width, height, shot, appHeight = 900, tilt = 3, enter = 1, children }: {
  left: number; top: number; width: number; height: number; shot: Shot; appHeight?: number; tilt?: number; enter?: number; children: ReactNode;
}) {
  return (
    <div style={{
      position: "absolute", left, top, width, height, overflow: "hidden", borderRadius: 12, boxShadow: "var(--shadow-pop)",
      opacity: enter, transform: `perspective(3200px) rotateX(${tilt}deg) translateY(${mix(enter, 60, 0)}px) scale(${mix(enter, 0.96, 1)})`, transformOrigin: "center top",
    }}>
      <div style={{ width: 1600, height: appHeight, position: "relative", background: "var(--bg)", fontSize: 14,
        transform: `scale(${shot.scale}) translate(${-shot.x}px, ${-shot.y}px)`, transformOrigin: "0 0" }}>
        {children}
      </div>
    </div>
  );
}

/** A shot that eases from `a` to `b` between two frames. */
export function useShot(a: Shot, b: Shot, start: number, dur: number, easing = INOUT): Shot {
  const t = useT(start, dur, easing);
  return { scale: mix(t, a.scale, b.scale), x: mix(t, a.x, b.x), y: mix(t, a.y, b.y) };
}

/** The pointer, with a ring that opens where it clicks. `clicks` are frames. */
export function Cursor({ x, y, clicks = [], opacity = 1 }: { x: number; y: number; clicks?: number[]; opacity?: number }) {
  const f = useCurrentFrame();
  const since = clicks.map((c) => f - c).filter((d) => d >= 0 && d < 16);
  const press = clicks.some((c) => f - c >= 0 && f - c < 4);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: 0, height: 0, opacity, pointerEvents: "none" }}>
      {since.map((d) => (
        <span key={d} style={{ position: "absolute", left: -18, top: -18, width: 36, height: 36, borderRadius: 999,
          border: "2px solid var(--accent)", opacity: 1 - d / 16, transform: `scale(${0.4 + d / 16})` }} />
      ))}
      <svg width="30" height="38" viewBox="0 0 15 19" style={{ position: "absolute", left: -2, top: -2, transform: `scale(${press ? 0.88 : 1})`, transformOrigin: "2px 2px" }}>
        <path d="M1 1 L1 15.5 L4.6 12.2 L7.2 17.8 L9.6 16.7 L7.1 11.2 L12.2 11.2 Z" fill="#fff" stroke="#171c21" strokeWidth="1.1" strokeLinejoin="round" />
      </svg>
    </div>
  );
}

/** Where the pointer is at this frame, along `path`: [frame, x, y] stops, eased between. */
export function usePath(path: [number, number, number][]) {
  const f = useCurrentFrame();
  const fs = path.map((p) => p[0]);
  const opts = { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: INOUT } as const;
  return { x: interpolate(f, fs, path.map((p) => p[1]), opts), y: interpolate(f, fs, path.map((p) => p[2]), opts) };
}

/** The wordmark path from web/src/Shell.tsx (the banner, cropped). */
const WORDMARK = "M446.92 199.96H446.22Q443.84 206.4 438.45 210.04Q433.06 213.68 425.78 213.68Q411.92 213.68 404.36 203.67Q396.8 193.66 396.8 175.6Q396.8 157.54 404.36 147.53Q411.92 137.52 425.78 137.52Q433.06 137.52 438.45 141.09Q443.84 144.66 446.22 151.24H446.92V108.4H462.18V212H446.92ZM430.4 200.52Q437.4 200.52 442.16 197.09Q446.92 193.66 446.92 188.06V163.14Q446.92 157.54 442.16 154.11Q437.4 150.68 430.4 150.68Q422.42 150.68 417.66 155.79Q412.9 160.9 412.9 169.3V181.9Q412.9 190.3 417.66 195.41Q422.42 200.52 430.4 200.52ZM484.02 212V139.2H499.28V153.2H499.98Q501.52 147.6 506.42 143.4Q511.32 139.2 520 139.2H524.06V153.9H518.04Q508.94 153.9 504.11 156.84Q499.28 159.78 499.28 165.52V212ZM545.34 126.18Q540.58 126.18 538.41 123.94Q536.24 121.7 536.24 118.2V115.82Q536.24 112.32 538.41 110.08Q540.58 107.84 545.34 107.84Q550.1 107.84 552.2 110.08Q554.3 112.32 554.3 115.82V118.2Q554.3 121.7 552.2 123.94Q550.1 126.18 545.34 126.18ZM537.64 139.2H552.9V212H537.64ZM590.28 212Q582.44 212 578.59 208.01Q574.74 204.02 574.74 196.88V108.4H590V199.54H600.08V212ZM629.34 212Q621.5 212 617.65 208.01Q613.8 204.02 613.8 196.88V108.4H629.06V199.54H639.14V212ZM661.4 126.18Q656.64 126.18 654.47 123.94Q652.3 121.7 652.3 118.2V115.82Q652.3 112.32 654.47 110.08Q656.64 107.84 661.4 107.84Q666.16 107.84 668.26 110.08Q670.36 112.32 670.36 115.82V118.2Q670.36 121.7 668.26 123.94Q666.16 126.18 661.4 126.18ZM653.7 139.2H668.96V212H653.7ZM719.36 213.68Q711.8 213.68 705.57 211.02Q699.34 208.36 695 203.39Q690.66 198.42 688.28 191.35Q685.9 184.28 685.9 175.6Q685.9 166.92 688.28 159.85Q690.66 152.78 695 147.81Q699.34 142.84 705.57 140.18Q711.8 137.52 719.36 137.52Q726.92 137.52 733.15 140.18Q739.38 142.84 743.72 147.81Q748.06 152.78 750.44 159.85Q752.82 166.92 752.82 175.6Q752.82 184.28 750.44 191.35Q748.06 198.42 743.72 203.39Q739.38 208.36 733.15 211.02Q726.92 213.68 719.36 213.68ZM719.36 201.08Q727.2 201.08 731.96 196.25Q736.72 191.42 736.72 181.76V169.44Q736.72 159.78 731.96 154.95Q727.2 150.12 719.36 150.12Q711.52 150.12 706.76 154.95Q702 159.78 702 169.44V181.76Q702 191.42 706.76 196.25Q711.52 201.08 719.36 201.08ZM769.76 212V139.2H785.02V151.24H785.72Q788.1 145.36 792.93 141.44Q797.76 137.52 806.16 137.52Q817.36 137.52 823.59 144.87Q829.82 152.22 829.82 165.8V212H814.56V167.76Q814.56 150.68 800.84 150.68Q797.9 150.68 795.03 151.45Q792.16 152.22 789.92 153.76Q787.68 155.3 786.35 157.68Q785.02 160.06 785.02 163.28V212Z";

/** The `drillion_` wordmark, `size` pixels tall, in the theme's accent; `cursor` fades the underscore. */
export function Wordmark({ size, cursor = 1 }: { size: number; cursor?: number }) {
  return (
    <svg viewBox="396 107 494 107" width={size * 494 / 107} height={size} role="img" aria-label="drillion" style={{ display: "block", flexShrink: 0 }}>
      <path fill="var(--accent)" d={WORDMARK} />
      <rect x="851.22" y="197.54" width="38.56" height="14.46" fill="var(--control-edge)" opacity={cursor} />
    </svg>
  );
}

export const label: CSSProperties = { fontSize: 12, fontWeight: 500, letterSpacing: "0.08em", color: "var(--text-muted)", textTransform: "uppercase" };
export const mono: CSSProperties = { fontFamily: "var(--font-mono)" };

/** An app point, in frame pixels, for a window at (`left`, `top`) looking through `shot`. */
export const toFrame = (shot: Shot, left: number, top: number, x: number, y: number) =>
  ({ x: left + (x - shot.x) * shot.scale, y: top + (y - shot.y) * shot.scale });

/** A rounded box that draws itself on around something, like a pen stroke: `t` is 0 → 1. */
export function Ring({ t, w, h, pad = 4 }: { t: number; w: number; h: number; pad?: number }) {
  return (
    <svg width={w + pad * 2 + 4} height={h + pad * 2 + 4} style={{ position: "absolute", left: -pad - 2, top: -pad - 2, overflow: "visible", pointerEvents: "none" }}>
      <rect x={2} y={2} width={w + pad * 2} height={h + pad * 2} rx={5} fill="none" stroke="var(--accent)" strokeWidth={2}
        pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} opacity={t ? 1 : 0} />
    </svg>
  );
}
