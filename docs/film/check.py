"""Compare every frame of the encoded AVIF with the render it came from.

`pnpm check` after `pnpm encode`. A 16 px block whose mean differs from the render by more
than `LIMIT` levels is a block the encoder left stale or smeared; ordinary AV1 loss at the
default CRF stays well under it.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

LIMIT = 12
FRAMES = sorted(Path("out/frames").glob("element-*.png"))
FILM = Path("../images/drillion-film.avif")


def blocks(a: np.ndarray, b: np.ndarray) -> float:
    d = np.abs(a.astype(np.int16) - b.astype(np.int16)).mean(axis=2)
    h, w = d.shape[0] // 16 * 16, d.shape[1] // 16 * 16
    return float(d[:h, :w].reshape(h // 16, 16, w // 16, 16).mean(axis=(1, 3)).max())


def main() -> int:
    film = Image.open(FILM)
    if film.n_frames != len(FRAMES):
        print(f"{FILM.name} has {film.n_frames} frames, the render has {len(FRAMES)}")
        return 1
    worst = []
    for i, frame in enumerate(FRAMES):
        film.seek(i)
        got = np.asarray(film.convert("RGB"))
        worst.append(blocks(got, np.asarray(Image.open(frame).convert("RGB"))))
    bad = [i for i, w in enumerate(worst) if w > LIMIT]
    mb = FILM.stat().st_size / 1e6
    print(
        f"{FILM.name}: {film.size[0]}x{film.size[1]}, {film.n_frames} frames, {mb:.1f} MB, "
        f"worst block {max(worst):.1f} at frame {int(np.argmax(worst))}, "
        f"{len(bad)} frames over {LIMIT}"
    )
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
