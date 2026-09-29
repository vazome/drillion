# The drillion film

The looping film at the top of the project README, made with [Remotion](https://www.remotion.dev):
React components rendered frame by frame. Each scene draws the real app with its own design-system
components, tokens, fonts and track marks from `web/`, so a UI change reaches the film on the next
render.

```bash
pnpm install
pnpm studio          # scrub every scene at http://localhost:3000
pnpm render          # every frame, as PNG, into out/frames
pnpm webp            # out/frames → ../images/drillion-film.webp
pnpm check           # every WebP frame against its render; fails on ghosting
```

`pnpm webp` takes a width and a frame rate, `1600 30` by default: the full render, lossless,
about 43 MB. `ffmpeg` with `libwebp_anim` does the encoding. Keep it lossless: lossy WebP skips
blocks it judges unchanged from the frame before, so a slow crossfade leaves the old scene
ghosting through the new one. Every re-encode stays in git history, so re-encode when the film
changes, not on a whim.

- `src/Film.tsx`: the scenes in order and their lengths, 30 frames a second.
- `src/scenes/`: one file per scene. Every motion is a function of the frame, never CSS
  animation, so each frame renders the same every time.
- `src/kit.tsx`: the shared pieces: captions, the camera window, the pointer, the easings.
- `src/Sidebar.tsx`, `src/Task.tsx`: the app's chrome, redrawn. When `web/src/Shell.tsx` or the
  task screen changes, these follow.

Captions state no counts, of tasks or of tracks: the film outlives the next task someone adds.
Numbers inside the app screens are fine, they are the UI as it looks.

Remotion is free for individuals and teams of up to three people; see its
[licence](https://www.remotion.dev/license).
