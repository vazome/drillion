"""Shared bits for exercises. Nothing to edit here."""

import os
import random


def rng():
    """Fresh data every sitting: the runner passes a new seed each time an
    exercise comes up, so the literal answer you memorised never fits."""
    seed = os.environ.get("DRILLION_SEED")
    return random.Random(int(seed) if seed else 7)
