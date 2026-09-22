"""What one sitting of 320 asks for, and what counts as having answered it.

hadolint already refuses a piped RUN with no pipefail (DL4006), so what `check` adds is
the part hadolint does not know: which shell, which URL, and that curl fails loudly."""

from itertools import pairwise

HELMS = ["3.16.4", "3.17.3", "3.18.4"]
BASE = "debian:bookworm-slim"


def brief(r):
    return {"helm": r.choice(HELMS)}


def _fails_loudly(words):
    """curl's -f, alone, in a cluster like -fsSL, or spelt --fail."""
    return any(
        w == "--fail" or (w.startswith("-") and not w.startswith("--") and "f" in w)
        for w in words
    )


def check(stages, b):
    assert len(stages) == 1, f"one stage is enough here: this file has {len(stages)}"
    stage = stages[0]
    assert stage["base"] == BASE, f"line {stage['line']}: FROM {BASE}"
    shells = stage.all("SHELL")
    assert shells, "set SHELL before the piped RUN, so a failed download fails the build"
    shell = shells[0]["exec"] or []
    assert shell[:1] == ["/bin/bash"] and shell[-1:] == ["-c"], (
        f"line {shells[0]['line']}: the shell is bash, run with -c: "
        '`SHELL ["/bin/bash", "-o", "pipefail", "-c"]`'
    )
    assert any(a == "-o" and c == "pipefail" for a, c in pairwise(shell)), (
        f"line {shells[0]['line']}: pass `-o pipefail` to the shell"
    )
    piped = [s for s in stage.all("RUN") if "|" in s["words"]]
    assert len(piped) == 1, "one RUN pipes the download into tar"
    run = piped[0]
    assert shells[0]["line"] < run["line"], (
        f"line {run['line']}: SHELL only changes the RUNs after it, and this one comes first"
    )
    words = run["words"]
    cut = words.index("|")
    fetch, unpack = words[:cut], words[cut + 1 :]
    assert fetch[:1] == ["curl"], f"line {run['line']}: download with curl, then pipe it into tar"
    assert _fails_loudly(fetch), (
        f"line {run['line']}: give curl -f, or a 404 page is what goes down the pipe"
    )
    url = f"https://get.helm.sh/helm-v{b['helm']}-linux-amd64.tar.gz"
    assert url in fetch, f"line {run['line']}: download {url}"
    assert unpack[:1] == ["tar"], f"line {run['line']}: the download is piped into tar"
    assert "/usr/local/bin" in unpack and "linux-amd64/helm" in unpack, (
        f"line {run['line']}: extract linux-amd64/helm into /usr/local/bin, and nothing else"
    )
    installs = [s for s in stage.all("RUN") if "install" in s["words"] and "curl" in s["words"]]
    assert installs and installs[0]["line"] < run["line"], (
        "install curl with apt-get, in a RUN before the one that uses it"
    )
    copies = [c for c in stage.all("COPY") if c["words"] and c["words"][0] == "deploy.sh"]
    assert copies and copies[0]["words"][-1] == "/usr/local/bin/deploy.sh", (
        "COPY deploy.sh /usr/local/bin/deploy.sh"
    )
    entry = stage.all("ENTRYPOINT")
    assert len(entry) == 1 and entry[0]["exec"] == ["deploy.sh"], (
        'one ENTRYPOINT, in exec form: ["deploy.sh"]'
    )
