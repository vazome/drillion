import base64


def solve(blobs, tokens):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    blobs = []
    # a blob only tells the two alphabets apart when it needs the 62nd or 63rd character
    for pad_case in (0, 1, 2, 0, 1, 2):
        while True:
            size = r.randrange(6, 22)
            blob = bytes(r.randrange(256) for _ in range(size - size % 3 + pad_case))
            if base64.urlsafe_b64encode(blob) != base64.b64encode(blob):
                blobs.append(blob)
                break
    tokens = [base64.urlsafe_b64encode(b).decode("ascii").rstrip("=") for b in blobs]
    return blobs, tokens


def _reference(blobs, tokens):
    encoded = [base64.urlsafe_b64encode(b).decode("ascii").rstrip("=") for b in blobs]
    decoded = [base64.urlsafe_b64decode(t + "=" * (-len(t) % 4)) for t in tokens]
    return encoded, decoded


def test_solve():
    r = rng()
    blobs, tokens = _gen(r)

    encoded, decoded = solve(blobs, tokens)
    want_encoded, want_decoded = _reference(blobs, tokens)

    assert len(encoded) == len(blobs), "one token per blob"
    for blob, got, want in zip(blobs, encoded, want_encoded):
        assert isinstance(got, str), f"{blob!r}: return str, not bytes"
        assert got == want, f"{blob!r} encoded"
        assert "=" not in got, f"{blob!r}: strip the padding"
        assert "+" not in got and "/" not in got, f"{blob!r}: use the URL-safe alphabet"

    assert len(decoded) == len(tokens), "one blob per token"
    for token, got, want in zip(tokens, decoded, want_decoded):
        assert got == want, f"{token!r} decoded"

    # the pair has to be each other's inverse, including for a token that lost two '='
    assert decoded == blobs, "decoding the wire tokens must give the original bytes back"
    assert any(len(t) % 4 == 2 for t in tokens), "generator should cover the two-'=' case"
    assert any(c in "-_" for t in tokens for c in t), "generator should cover the URL-safe characters"
