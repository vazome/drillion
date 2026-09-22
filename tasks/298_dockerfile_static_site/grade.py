"""What one sitting of 298 asks for, and what counts as having answered it.

`check` follows the site: the lockfile in first, `npm ci`, the build, and only `dist/`
crossing into the nginx stage."""

NODES = ["22", "24"]
NGINX = ["1.27-alpine", "1.28-alpine", "1.29-alpine"]


def brief(r):
    return {"node": r.choice(NODES), "nginx": r.choice(NGINX)}


def _all(stage, cmd):
    return [s for s in stage["steps"] if s["cmd"] == cmd]


def _npm(stage, *words):
    return [s for s in _all(stage, "RUN") if "npm" in s["words"] and all(w in s["words"] for w in words)]


def check(stages, b):
    assert len(stages) == 2, f"two stages, one to build and one to serve: this file has {len(stages)}"
    build, final = stages
    assert build["base"] == f"node:{b['node']}-slim", (
        f"the build stage is FROM {build['base']!r}, and it should be 'node:{b['node']}-slim'"
    )
    assert build["name"], "name the build stage, `FROM ... AS build`, so the next one can copy from it"
    assert not _npm(build, "install") and not _npm(build, "i"), (
        "`npm install` may rewrite the lockfile and install something else; `npm ci` installs "
        "exactly what package-lock.json says, or fails"
    )
    ci = _npm(build, "ci")
    assert len(ci) == 1, "install the dependencies with one `RUN npm ci`"
    ci = ci[0]
    copies = _all(build, "COPY")
    manifests = [c for c in copies if c["line"] < ci["line"]]
    assert manifests and sorted(manifests[0]["words"][:-1]) == ["package-lock.json", "package.json"], (
        "copy package.json and package-lock.json on their own before `npm ci`, so the install "
        "is cached until they change"
    )
    assert all(c["words"][:-1] in (["package.json", "package-lock.json"], ["package-lock.json", "package.json"]) for c in manifests), (
        f"line {manifests[-1]['line']}: only the two package files are copied before `npm ci`"
    )
    built = _npm(build, "run", "build")
    assert len(built) == 1, "build the site with `RUN npm run build`"
    source = [c for c in copies if c["line"] > ci["line"]]
    assert source and source[0]["line"] < built[0]["line"], (
        "copy the rest of the source after `npm ci` and before `npm run build`"
    )
    served = f"nginxinc/nginx-unprivileged:{b['nginx']}"
    assert final["base"] == served, (
        f"the serving stage is FROM {final['base']!r}, and it should be {served!r}"
    )
    assert not _all(final, "RUN"), "the serving stage runs nothing: the site is already built"
    over = [c for c in _all(final, "COPY") if c["flags"].get("from") == build["name"]]
    assert len(over) == 1 and len(_all(final, "COPY")) == 1, (
        f"the serving stage copies one thing, `--from={build['name']}`: the built site"
    )
    src, dest = over[0]["words"][0].rstrip("/"), over[0]["words"][-1].rstrip("/")
    assert src.endswith("/dist") and len(over[0]["words"]) == 2, (
        f"line {over[0]['line']}: copy the dist folder the build wrote, and nothing else"
    )
    assert dest == "/usr/share/nginx/html", (
        f"line {over[0]['line']}: nginx serves /usr/share/nginx/html, not {dest}"
    )
    exposed = [w for s in _all(final, "EXPOSE") for w in s["words"]]
    assert exposed in (["8080"], ["8080/tcp"]), (
        "EXPOSE 8080: the unprivileged nginx listens there, since port 80 needs root"
    )
