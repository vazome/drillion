# The drillion film

The looping film at the top of the project README, made with [Remotion](https://www.remotion.dev):
React components rendered frame by frame. Each scene draws the real app with its own design-system
components, tokens, fonts and track marks from `web/`, so a UI change reaches the film on the next
render.

```bash
pnpm install
pnpm studio          # scrub every scene at http://localhost:3000
pnpm render          # every frame, as PNG, into out/frames
pnpm encode          # out/frames → ../images/drillion-film.avif and its still poster
pnpm check           # every AVIF frame against its render; fails on stale or smeared blocks
```

`pnpm encode` takes a CRF, `18` by default: about 2.3 MB for the whole film, and at 3x zoom
its worst frame still matches the render. Held shots cost almost nothing; a camera that
creeps costs every frame. What it writes, and why:

- **Animated AVIF, AV1 in 4:4:4.** Full colour resolution keeps coloured UI text sharp; 4:2:0
  smears it. AV1 predicts each frame from the decoded one before, so a fade cannot leave the
  old scene behind. Chrome 85+, Firefox 93+ and Safari 16.4+ play it, and GitHub serves
  `.avif` as `image/avif`.
- **Colour tagged** BT.709, sRGB transfer, full range. ffmpeg leaves AVIF untagged otherwise,
  and browsers then guess.
- **A still poster**, `drillion-film-still.png`, frame `POSTER` in `encode.mjs`. The README
  shows it to anyone whose system asks for reduced motion, and to browsers without animated
  AVIF. GitHub's own pause control and reduced-motion handling only cover GIFs it marks as
  animated, so the `<picture>` does it.

Not animated WebP. libwebp's lossy animation encoder compares each frame with the previous
*source* frame and skips pixels within a quality-based tolerance, while the decoder still shows
older pixels there; keyframes, which would reset that, are off by default and ffmpeg cannot turn
them on. A slow crossfade then leaves the old scene showing through the new one. libwebp fixed
it on its main branch in August 2025 ("canvas carryover"), after 1.6.0, its latest release.
Lossless WebP avoids it but costs about 43 MB. Not GIF (256 colours), APNG (about 94 MB),
JPEG XL (Safari shows stills only) or video (GitHub strips `<video>`).

Every encode stays in git history, so encode when the film changes, not on a whim.

- `src/Film.tsx`: the scenes in order and their lengths, 30 frames a second.
- `src/scenes/`: one file per scene. Every motion is a function of the frame, never CSS
  animation, so each frame renders the same every time.
- `src/kit.tsx`: the shared pieces: captions, the camera window, the pointer, the easings.
- `src/Sidebar.tsx`, `src/Task.tsx`: the app's chrome, redrawn. When `web/src/Shell.tsx` or the
  task screen changes, these follow.

Captions state no counts, of tasks or of tracks: the film outlives the next task someone adds.
Numbers inside the app screens are fine, they are the UI as it looks.

## Motion rules

The film is read at about 880 px wide on github.com, looping. These keep it composed:

- **Frame on gutters.** A shot's visible app range (`x` to `x + width / scale`) starts and ends
  in the space between panels, never through text, a card or a border. No slivers of a
  neighbouring column at the edge.
- **Hold still to read.** The camera moves only when the action calls for it (following the
  code down to Submit), then stops. Each scene holds its finished state for about a second
  before the crossfade.
- **One caption at a time.** `Caption` arrives after the crossfade in and leaves before the one
  out (`SceneFrames` tells it the scene's length). It sits on the window's left edge.
- **One springy thing.** Entrances use a critically damped spring; the rung climbing the
  ladder in Climb is the only bounce.
- **The pointer behaves like a hand.** It fades in and out, travels in an arc, pauses before a
  click, and aims beside the label it clicks, not on it. A click that opens something is a
  reason to cut.
- **The loop has no seam.** The end card sheds everything but the wordmark, which glides to
  where Open draws it, and the last frames dissolve into Open's first frame, so the last
  frame and the first are the same picture.

Remotion is free for individuals and teams of up to three people; see its
[licence](https://www.remotion.dev/license).
