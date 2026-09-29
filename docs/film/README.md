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
```

`pnpm webp` takes a width, a quality and a frame rate, `1024 60 20` by default: about 5 MB,
and sharp at the width GitHub shows a README. `ffmpeg` with `libwebp_anim` does the encoding.

- `src/Film.tsx`: the scenes in order and their lengths, 30 frames a second.
- `src/scenes/`: one file per scene. Every motion is a function of the frame, never CSS
  animation, so each frame renders the same every time.
- `src/kit.tsx`: the shared pieces: captions, the camera window, the pointer, the easings.

Remotion is free for individuals and teams of up to three people; see its
[licence](https://www.remotion.dev/license).
