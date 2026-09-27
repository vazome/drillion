"""What one sitting of 346 asks for: a merge that stops on a real conflict, finished by
hand rather than abandoned.

The answer is the repository's end state: the branch folded into main with git's default
message, the config file holding exactly what it should, nothing left mid-merge."""


def brief(r):
    mine, theirs, port = r.sample(range(8001, 8099), 3)
    return {
        "topic": r.choice(["metrics", "admin"]),
        "mine": mine,
        "theirs": theirs,
        "port": port,
        "workers": r.randint(2, 8),
    }


def setup(repo, b):
    t = b["topic"]
    repo.commit("add the server config", {"config.ini": "[server]\nport = 8000\nworkers = 1\n"})
    repo.git("switch", "-q", "-c", f"feature/{t}")
    repo.commit(f"move {t} to its own port", {"config.ini": f"[server]\nport = {b['theirs']}\nworkers = 1\n"})
    repo.git("switch", "-q", "main")
    repo.commit("scale the server", {"config.ini": f"[server]\nport = {b['mine']}\nworkers = {b['workers']}\n"})
