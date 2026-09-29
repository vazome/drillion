"""Compare every frame of the encoded WebP with the render it came from, and fail on ghosting.

`pnpm check` after `pnpm webp`. A 16 px block whose mean differs from the render by more than
`LIMIT` levels is a block the encoder left stale or smeared.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

LIMIT = 4
FRAMES = sorted(Path("out/frames").glob("element-*.png"))
FILM = Path("../images/drillion-film.webp")


def blocks(a: np.ndarray, b: np.ndarray) -> float:
    d = np.abs(a.astype(np.int16) - b.astype(np.int16)).mean(axis=2)
    h, w = d.shape[0] // 16 * 16, d.shape[1] // 16 * 16
    return float(d[:h, :w].reshape(h // 16, 16, w // 16, 16).mean(axis=(1, 3)).max())


def main() -> int:
    film = Image.open(FILM)
    step, t, worst = 1000 / 30, 0.0, []
    for i in range(film.n_frames):
        film.seek(i)
        got = film.convert("RGB")
        want = Image.open(FRAMES[min(len(FRAMES) - 1, round(t / step))]).convert("RGB")
        if want.size != got.size:
            want = want.resize(got.size, Image.Resampling.LANCZOS)
        worst.append(blocks(np.asarray(got), np.asarray(want)))
        t += film.info.get("duration", step)
    bad = [i for i, w in enumerate(worst) if w > LIMIT]
    mb = FILM.stat().st_size / 1e6
    print(
        f"{FILM.name}: {film.size[0]}x{film.size[1]}, {film.n_frames} frames, {mb:.1f} MB, "
        f"worst block {max(worst):.1f}, {len(bad)} frames over {LIMIT}"
    )
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
