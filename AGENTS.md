# drillion

drillion is an Open Source platform to learn Python programming language through practice tasks.

It draws inpsiration from Exercism and Hackerank, but implements its own pragmatic approch.

## What so special about drillion?

drillion can be used by any number of users. It came to from the frustration around language learning platforms, all of the graphical unncesesaries, social rankings and over the top gamification. These are the points we consider non-negotiable.

1. Always open source
This is not "raise money", learn python in 30 days, "here is a voucher" platform. Everybody can freely use drillion and contribute.

2. Categorical pragmatism
People use drillion for only one single purpose - to get better at Python. drillion aids them, by clearly tagging pracises with respective topics names, people can easly search across topics and tasks. Transparency is key to understanding.

3. Local ready
drillion is a Docker image: one `docker run` and the client is available with a ready environment. A checkout is the contributors' dev loop, not a way to use drillion. There is no login or registration. Convenience is important factor to consistent learning. We must make sure that it stays this way. Upgrades should not be a concern, learning progress must be kept regardless of distribution line.

4. UX/UI that corresponds
UX: the system design must reflect the spaced repetition learning (a fixed Leitner ladder; `docs/adr/0001-leitner-not-fsrs.md` says why not FSRS). It's not 1 task - 1 topic. Topics must span across multiple tasks, topics must merge to ensure consistent learning of new concepts and preserving previosly learned material. Another example if takes user more than 30 minutes on the task without submission, drillion must pop notify them of taking a hint, you can't bruteforce something you are unaware of.
UI: When new UI component needs to be drawn for the client, you request it from the developer. Then you will be provided with it, so you can integrate it. Drawing UI is not your concern.  

## A note from the Developer

I like ambitious ideas, simple systems, and software that feels obvious. Do not preserve complexity just because it already exists. Do not introduce machinery because it looks architecturally impressive. Understand the real constraint, then fight for the smallest model that makes the correct behavior unsurprising.

Channel both "measure twice, cut once" and "yagni". Fight scope creep. Try to honor the dev's intent in both a minimal and realistic fashion.

Consider this document proper default, there are not a hard rules, it's the values we honor. Developer's preferences if present are the overrides.

## Brief glossary

**you** means the agent reading this file and changing drillion.
**we, us, and maintainers** mean vazome and other open-source developers building drillion. These are who you are talking to now.
**user or people** means the person using drillion to direct coding agents.
**client** means the web.
**environment** means one running drillion and the machine, filesystem, and state it has.
**project** means an environment-local workspace record rooted at a directory.

## Hit every surface

The most common defect in this repo is a change that works on the path you tested and is missing everywhere else. Before calling frontend work done, walk this list and say which entries applied:

- **Entry points.** A behavior reachable from one screen is often reachable from another too: the catalogue, a task, its lineage panel, Settings, and a keybinding. Fixing one is not fixing the feature.
- **Clients.** Web.
- **Reverse states.** If you added a way in, add the way out and the way to see it. Snooze needs unsnooze. Close needs reopen. A one-way door is a bug.
- **Run modes.** The Docker image is the product; `uv run drillion` from a checkout is the dev loop, and the two differ in data root, tools directory and bind address. Verify in the image, since only it is what learners run.

## Taste

- We use `ruff`. Build should not fail ruff.
- We use `uv` both in the environment and during docker image building.
- Conventional commit titles, plain language: `fix(web): submission no longer causes crashes`.
- Docs screenshots live in `docs/images/` and are linked by absolute
  `raw.githubusercontent.com/.../main/...` URL — never a tag, never relative. See
  `CONTRIBUTING.md`.
- Comments describe how a thing is used, and move when the code moves. To be used mostly to describe functions, not to annotate every line of behavior.
- If a rule here fights the task in front of you, say so loudly and get a human sign-off before breaking it.

### Creating Pull Requests

Never push to `main`, and never force-push a branch someone else may have pulled.

Work out where to push **once**, with `git remote -v`. There are two shapes, and only one of
them involves a fork:

- **You can push to `vazome/drillion` directly** — it is `origin`, and there is no `upstream`.
  This is a maintainer's own clone, and it is the common case. Push the feature branch to
  `origin` and open the PR against `origin/main`. Do **not** fork, and do **not** add an
  `upstream` remote pointing at the repo `origin` already points at.
- **You cannot** — then `origin` is your fork and `upstream` is `vazome/drillion`. Push to
  `origin`, never to `upstream`. If the fork remote is missing:

  ```bash
  gh repo fork vazome/drillion --remote --remote-name origin
  ```

Either way, the remote you open the PR against is the **canonical remote**: `upstream` when a
fork is in play, `origin` otherwise. If the remotes match neither shape, say so and ask before
renaming anything.

Before pushing, perform a self-review of your changes, then rebase onto the latest target
branch (usually `main`) so CI runs against up-to-date code:

```bash
git fetch <canonical-remote> <target-branch>
git rebase <canonical-remote>/<target-branch>
```

If there are conflicts, resolve them and continue the rebase. If the rebase is too complex,
ask the user for guidance.

Remind the user to:

1. Review the PR title — a conventional title with a scope, the same shape as the commits inside it: `fix(web): submission no longer causes crashes`. Short (under 70 chars), imperative, and about user impact rather than implementation.
2. Add a brief description of the changes at the top of the body.
3. Reference related issues when applicable.

## Boundaries

- **Ask first**
  - Large cross-package refactors.
  - New dependencies with broad impact.
  - Destructive data or migration changes.
- **Never**
  - Commit secrets, credentials, or tokens.
  - Edit generated files by hand when a generation workflow exists.
  - Use destructive git operations unless explicitly requested.

### Do not tag individuals

Don't @-mention contributors or maintainers by GitHub username unless a human asks you to.
Refer to roles, code ownership, labels or components instead: a mention notifies someone
who didn't choose to join the thread. Replying to people already in the same PR or issue
thread is fine.

## Additional tips

- Don't verify with browsers or computer use unless the user explicitly agrees or requests it.
- Security is important, but should not be over-indexed on, especially for dev features.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on `vazome/drillion`, driven with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, each label string equal to its name. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` plus `docs/adr/` at the repo root. See `docs/agents/domain.md`.
