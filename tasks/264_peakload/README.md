---
title: monotonic deque — the peak in every rolling window, and the minute it happened
difficulty: medium
tier: core
minutes: 18
prereqs: [60, 140]
tags: [deque, sequences]
---
# monotonic deque — the peak in every rolling window, and the minute it happened

*A deque that only ever holds candidates worth remembering: each window's answer is already sitting at its front.*

## Read first
- [`collections.deque`](https://devdocs.io/python~3.14/library/collections#collections.deque) — `append`, `pop`, `popleft` and reading `dq[0]` / `dq[-1]`, which is the whole toolkit
- [`enumerate`](https://devdocs.io/python~3.14/library/functions#enumerate) — you keep *positions*, not values, because a position is what tells you when a candidate has aged out
- [`max`](https://devdocs.io/python~3.14/library/functions#max) — the answer you check yourself against on small input
- [`list.index`](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — worth reading closely enough to see why it is the wrong tool here

## Why
Capacity planning wants one line per rolling window: over any five consecutive minutes of last week, what was the highest concurrent request count, and when? The peak sizes the machine; the minute it happened is what you take to the incident review, because "the worst five minutes were the ones around the batch job" is an answer and "the worst was 900" is not.

Recomputing `max` over each window re-reads almost the same minutes for every window, and a week of per-minute data with an hour-long window is ten thousand readings read sixty times each. The way out is to notice what you never need again: the moment a newer reading is at least as high as an older one still in the window, the older one can never be the answer for any future window, because the newer one outlives it and is at least as big. Throw it away on the spot, and what is left is a short list of candidates in decreasing order — so the current window's peak is whatever sits at the front.

## You get
- `load` — a list of `int`, one reading per minute, in order. At least one reading.
- `window` — an `int`, how many consecutive minutes a window covers. `1 <= window <= len(load)`.

## You return
A `list` of `(minute, peak)` tuples, one per window, left to right: `minute` is the index into `load` where that window's highest reading sits, and `peak` is the reading.

## Rules
- there are `len(load) - window + 1` windows, the first covering minutes `0` to `window - 1`
- on a tie inside a window, report the **earliest** minute that holds the peak
- `minute` is an index into the whole of `load`, not an offset inside the window
- `window == 1` gives one entry per minute, each pointing at itself
- readings repeat. A window can be entirely one value
- `load` comes back untouched
- each reading enters and leaves your bookkeeping once. `max(load[i:i + window])` per window is right and is the thing being replaced

```python
solve([4, 1, 7, 7, 2], 3)
# -> [(2, 7), (2, 7), (2, 7)]
solve([5, 1, 5], 2)
# -> [(0, 5), (2, 5)]
solve([9, 8], 1)
# -> [(0, 9), (1, 8)]
```

> [!WARNING]
> `load.index(max(window_slice))` looks like it answers the "when" half and it does not: `index` searches from the start of the whole list, so the second window of `[5, 1, 5]` reports minute `0` — a minute that is not in that window at all. That is the second example above, and it is the submission this task rejects most often. Whatever you keep, keep it in terms of positions in `load`.

> [!NOTE]
> Discard an older candidate only when the new reading is **strictly** greater. Discard on equal too, and you keep the later of two equal peaks, which breaks the earliest-minute tie rule.

## Hints
### Hint 1
Hold a `deque` of **indexes** into `load`, kept so that the readings they point at decrease from front to back. Then `dq[0]` is always the index of the largest reading among the candidates, and every index in the deque is bigger than the one before it, so ageing out happens at the front and arrivals happen at the back.

### Hint 2
One pass over `enumerate(load)`, three things per reading, in this order:

1. pop from the **back** while the reading at `dq[-1]` is strictly less than the new one — those can never win again
2. append the new index
3. if `dq[0]` has fallen out of the window (its index is `<= i - window`), `popleft` it — at most one can expire per step

Then, once `i >= window - 1`, a window has just completed and `dq[0]` is its answer.

### Hint 3
The same deque, run the other way for the other question — the *floor* of every window, which is what a "did throughput ever dip below X" alert needs:

```python
from collections import deque

def window_floors(values, size):
    dq, out = deque(), []
    for i, value in enumerate(values):
        while dq and values[dq[-1]] > value:    # ">" instead of "<": the only change
            dq.pop()
        dq.append(i)
        if dq[0] <= i - size:
            dq.popleft()
        if i >= size - 1:
            out.append(values[dq[0]])
    return out

window_floors([4, 1, 7, 7, 2], 3)   # -> [1, 1, 2]
```

One comparison flips the whole thing round. It is worth reading the invariant out loud — "the deque is decreasing" becomes "the deque is increasing" — and checking that ageing out at the front still makes sense.
