# Drillion

Drillion is an Open Source platform to learn Python programming language through practice excersises.

It draws inpsiration from Exercism and Hackerank, but implements its own pragmatic approch.

## What so special about Drillion?

Drillion can be used by any number of users. It came to from the frustration around language learning platforms, all of the graphical unncesesaries, social rankings and over the top gamification. These are the points we consider non-negotiable.

1. Always open source
This is not "raise money", learn python in 30 days, "here is a voucher" platform. Everybody can freely use Drillion and contribute.

2. Categorical pragmatism
People use drillion for only one single purpose - to get better at Python. Drillion aids them, by clearly tagging pracises with respective topics names, people can easly search across topics and tasks. Transparency is key to understanding.

3. Local ready
The architecture of Drillion allows to either clone the repo and self-deploy or docker run, so the client become available with ready environment. There is no login or registration. Convenience is important factor to consistent learning. We must make sure that it stays this way. Upgrades should not be a concern, learning progress must be kept regardless of distribution line.

4. UX/UI that corresponds
UX: the system design must reflect the spaced repetition learning (FSRS). It's not 1 task - 1 topic. Topics must span across multiple tasks, topics must merge to ensure consistent learning of new concepts and preserving previosly learned material. Another example if takes user more than 30 minutes on the task without submission, Drillion must pop notify them of taking a hint, you can't bruteforce something you are unaware of.
UI: When new UI component needs to be drawn for the client, you request it from the developer. Then you will be provided with it, so you can integrate it. Drawing UI is not your concern.  

## A note from the Developer

I like ambitious ideas, simple systems, and software that feels obvious. Do not preserve complexity just because it already exists. Do not introduce machinery because it looks architecturally impressive. Understand the real constraint, then fight for the smallest model that makes the correct behavior unsurprising.

Channel both "measure twice, cut once" and "yagni". Fight scope creep. Try to honor the dev's intent in both a minimal and realistic fashion.

Consider this document proper default, there are not a hard rules, it's the values we honor. Developer's preferences if present are the overrides.

## Brief glossary

**you** means the agent reading this file and changing Drillion.
**we, us, and maintainers** mean vazome and other open-source developers building Drillion. These are who you are talking to now.
**user or people** means the person using Drillion to direct coding agents.
**client** means the web.
**environment** means one running Drillion and the machine, filesystem, and state it has.
**project** means an environment-local workspace record rooted at a directory.

## Hit every surface

The most common defect in this repo is a change that works on the path you tested and is missing everywhere else. Before calling frontend work done, walk this list and say which entries applied:

- **Entry points.** A behavior reachable from the chat view is usually also reachable from Settings, the command palette, and a keybinding. Fixing one is not fixing the feature.
- **Clients.** Web.
- **Reverse states.** If you added a way in, add the way out and the way to see it. Snooze needs unsnooze. Close needs reopen. A one-way door is a bug.
- **Connection modes.** Local, remote/relay, and tunnel behave differently. Multi-device and multi-environment cases are real.

## Taste

- We use `ruff`. Build should not fail ruff.
- We use `uv` both in the environment and during docker image building.
- Conventional commit titles, plain language: `fix(web): submission no longer causes crashes`.
- Comments describe how a thing is used, and move when the code moves. To be used mostly to describe functions, not to annotate every line of behavior.
- If a rule here fights the task in front of you, say so loudly and get a human sign-off before breaking it.

### Creating Pull Requests

**Always push to the user's fork (`origin`)**, not to `upstream` or "GitHub".
Never push directly to `main`.

Before pushing, confirm the remote setup matches the conventions above
(`upstream` → `vazome/drillion`, `origin` → your fork). Run `git remote -v` and,
if the names don't match, propose renames as described in "Git remote naming
conventions" — ask the user to confirm before running them.

If the fork remote does not exist at all, create one:

```bash
gh repo fork vazome/drillion --remote --remote-name origin
```

Before pushing, perform a self-review of your changes.

Before pushing, always rebase your branch onto the latest target branch (usually `main`)
to avoid merge conflicts and ensure CI runs against up-to-date code:

```bash
git fetch upstream <target_branch>
git rebase upstream/<target_branch>
```

If there are conflicts, resolve them and continue the rebase. If the rebase is too complex,
ask the user for guidance.
```

Remind the user to:

1. Review the PR title — keep it short (under 70 chars), in the imperative mood, and focused on user impact. Do not use Conventional Commits prefixes (`fix:`, `feat:`, `chore:`, …).
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

AI agents MUST NOT mention or tag individual contributors, committers,
PMC members, or maintainers using GitHub usernames (e.g. `@user`) unless
explicitly instructed by a human reviewer. When suggesting who might be
relevant to a discussion, refer to roles, teams, code ownership
information, labels, or components instead of individuals. This keeps
notification noise down and avoids pulling people into threads they have
not chosen to join.

The only exceptions are mentions a human has explicitly authorized —
including the `@<github-handle>` in the `Drafted-by: … reviewed by
@<handle>` footer above, which names the reviewer who approved the
message — and replying within a thread to people already actively
participating in that same PR/issue discussion.

## Additional tips

- Don't verify with browsers or computer use unless the user explicitly agrees or requests it.
- Security is important, but should not be over-indexed on, especially for dev features.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on `vazome/study`, driven with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, each label string equal to its name. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` plus `docs/adr/` at the repo root. See `docs/agents/domain.md`.
