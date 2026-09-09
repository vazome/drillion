# Where the next hundred tasks come from

Research note, 2026-09-09. Scope: open-source collections of Python problems that drillion could
adapt to cover concepts the 189-task catalogue does not practise today. **Exercism is out of
scope** — 89 tasks already adapt it and this note proposes none.

Every licence below was read from the repository's own `LICENSE` file (via
`gh api repos/<owner>/<repo>/license`), the dataset card, or the site's own copyright page — never
from a summary. Every recommendation is judged against AGENTS.md: categorical pragmatism, YAGNI,
and the folder contract in [authoring-tasks.md](../authoring-tasks.md).

## 1. Verdict

The catalogue is not short of *tasks*. It is short of *surface*. 189 tasks carry 81 tags, and the
whole of Python's object model past `@property` — descriptors, ABCs, `__slots__`, the iterator
protocol written as a class, operator overloading, MRO — is absent. So is roughly thirty of the
standard library: no `struct`, no `sqlite3`, no `decimal`, no `bytes`/encodings, no `ipaddress`, no
`zoneinfo`, no `queue`, no `graphlib`. And so are the classical algorithms: one memoised recursion
(`188_knapsack`), one hand-rolled topological sort (`103_deporder`), and nothing else — no graph
traversal, no backtracking, no string-distance work.

Three of those are three different gaps, and no single source fills more than one:

- **algorithms** → `TheAlgorithms/Python` (MIT). Reference implementations already written and
  doctested; drillion writes the statement.
- **the object model** → `fluentpython/example-code-2e` (MIT), with `python_koans` (MIT) as a
  second seam for the gotcha-shaped tasks (`044_mutabledefault`, `053_copy`).
- **the standard library** → the CPython documentation's own examples, which are **Zero-Clause
  BSD**. Not a collection of exercises, but it is the only permissively-licensed well that has
  `struct`, `sqlite3` and `zoneinfo` in it at all.

MBPP is a fourth, weaker option: 974 problems, CC-BY-4.0, precedent already in `NOTICE` via
`187_job_spacing`, but mostly restating things the catalogue teaches twice already.

Almost everything else fails the licence gate, and it fails it hard. Project Euler is
CC BY-NC-SA 4.0, Rosetta Code is GFDL 1.2, CS50P is CC BY-NC-SA 4.0, Advent of Code says "free to
use, not free to copy", and both of Beazley's courses are CC BY-SA 4.0. The big code-benchmark
datasets — APPS, CodeContests, Project CodeNet — carry a permissive licence *on the repository*
while the problem statements inside it were scraped from Codeforces, AtCoder and Kattis. That is a
licence on the wrong thing, and it is the single most common trap in this space.

## 2. What the catalogue does not practise

Read from `tags:`, `tier:` and titles across all 189 `tasks/*/README.md`. Tiers today:
155 `core`, 19 `advanced`, 15 `packages`.

PR #221 adds 12 tasks giving all 29 single-exposure tags a second context, so **thin** concepts are
deliberately not the subject here. Everything below is *absent* — no task carries the tag and no
task's rules make you meet the idea in passing.

### 2.1 The object model past `@property`

The single largest hole, and the one that maps onto the thinnest tier. `057_classes` reaches
`__init__`/`__repr__`/`@property`; `160_clock` and `165_robot_simulator` reach rich comparisons and
`__eq__`. Past that:

| absent | what a task would look like |
|---|---|
| descriptors (`__get__`, `__set__`, `__set_name__`) | a validating field that several attributes reuse |
| `abc.ABC` / `@abstractmethod` | a plugin base that refuses to instantiate half-built |
| `typing.Protocol`, structural typing | duck-typing made checkable without inheritance |
| `__slots__` | the same class with and without, and what breaks |
| iterator protocol as a class (`__iter__`/`__next__`) | 5 generator tasks, zero written as a class |
| `__enter__`/`__exit__` on a class | `073_contextmanager` is `@contextmanager` only |
| `__add__`/`__radd__`/`__hash__`/`__len__`/`__contains__`/`__getitem__` | operator overloading proper |
| `__getattr__` / dynamic attributes | a config object that answers dotted paths |
| MRO and cooperative `super()` | `173_inheritance` is single inheritance |
| `__init_subclass__`, metaclasses | a registry that fills itself |
| generator `send()`/`throw()`/`close()` | the coroutine half of `yield` |
| `NamedTuple`, `namedtuple`, `TypedDict` | 2 `dataclasses` tasks, no tuple-shaped record |
| `TypeVar`, `Generic`, `@overload` | `047_typehints` reads hints, never writes generic ones |
| `weakref`, `contextvars` | niche, but genuinely nowhere |

### 2.2 The standard library

Absent outright, ordered by how plausibly a drillion learner meets them:

`struct` · `sqlite3` · `decimal` · `fractions` · `statistics` · `random` (seeded) · `secrets` ·
`uuid` · `base64`/`binascii` · `bytes`/`bytearray`/`memoryview`/`codecs` and text encoding ·
`ipaddress` · `urllib.parse` · `zoneinfo` and timezone arithmetic · `textwrap` · `difflib` ·
`shlex` · `fnmatch` · `configparser` · `tomllib` · `zipfile`/`tarfile`/`gzip` · `pickle` ·
`operator` · `queue.Queue` · `multiprocessing` proper · `signal`/`atexit` · `socket` ·
`unicodedata` · `array` · `graphlib` · `dis`.

Two of those sting more than the rest. `065_datetime` does `strptime` and deltas with no timezone
anywhere, which is where every real datetime bug lives. And `103_deporder` hand-rolls a topological
sort that `graphlib.TopologicalSorter` does in four lines — a perfect "now do it the boring way"
second context.

### 2.3 Algorithms and data structures

`188_knapsack` (memoised recursion), `171_binary_search`, `178_bisect`, `174_heapqmerge`,
`103_deporder`, `143_flatten_array`, `099_configdiff`. That is the lot. Absent:

graph traversal (BFS/DFS, shortest path, cycle detection as its own subject) · union-find ·
dynamic programming beyond one memoised recursion (edit distance, LCS, coin change as DP rather
than `168_change`'s greedy) · backtracking · sliding window and two pointers as named techniques ·
tries · prefix sums · matrix work (rotate, spiral, transpose beyond `154_transpose`) · number
theory (gcd, modular arithmetic, combinatorics).

Whether drillion *wants* this is a judgement call, not a fact — see §5.

### 2.4 Not a gap

Well covered, do not go looking: `asyncio` and concurrency (8 tasks each), HTTP and `requests`
(6), `boto3` (4), LangChain (6), testing and mocking (5), sets (8), dicts (8), strings (7).

## 3. The candidates

### 3.1 TheAlgorithms/Python — **adopt**

<https://github.com/TheAlgorithms/Python> · **MIT** · verified from `LICENSE.md` via the API.

Roughly 1,200 algorithm implementations across `graphs/`, `dynamic_programming/`,
`data_structures/` (trie, disjoint_set, heap, linked_list, stacks, queues, suffix_tree, kd_tree),
`backtracking/`, `bit_manipulation/`, `searches/`, `sorts/`, `strings/`, `ciphers/`, `matrix/`,
`greedy_methods/`, `divide_and_conquer/`, `maths/`.

**Fit: excellent, in an unusual way.** It is not a problem set — it has no statements. It has
*reference implementations*, most of them doctested, which is precisely the artefact
`_reference()` needs and the artefact every other source makes you write. drillion supplies the
`## Why`, the `## Rules` and the `_gen()`; the algorithm is already correct and already tested.
That inverts the usual adaptation cost and it also sidesteps the text-copying question entirely,
because no task text is copied.

**Attribution.** MIT permits adaptation and redistribution, requiring the copyright and permission
notice to travel with any substantial portion. A drillion task whose `_reference` is a rewrite of
their implementation should carry `source: TheAlgorithms/Python graphs/breadth_first_search (MIT,
adapted)` and the closing line, on the same reasoning `187_job_spacing` carries MBPP's.

**Yield: 40–60 tasks.** Filtered hard: skip `machine_learning/`, `neural_network/`, `quantum/`,
`physics/`, `financial/`, `computer_vision/` — none is 10–30 minutes and most need numpy.

> [!WARNING]
> Skip `project_euler/` entirely. Those 100+ files are MIT-licensed *code*, but the problems they
> solve are Project Euler's and their statements are CC BY-NC-SA 4.0 (§4.1). Adapting the code is
> fine; restating the problem is not.

**Fills:** §2.3 nearly in full, plus `array`, `operator` and `graphlib` from §2.2.

### 3.2 fluentpython/example-code-2e — **adopt**

<https://github.com/fluentpython/example-code-2e> · **MIT** · verified from `LICENSE` via the API.

The example code for *Fluent Python, 2nd ed.*, laid out one directory per chapter and mapping onto
§2.1 with almost indecent precision: `13-protocol-abc`, `16-op-overloading`, `22-dyn-attr-prop`,
`23-descriptor`, `24-class-metaprog`, `11-pythonic-obj` (`__slots__`, `__hash__`),
`12-seq-hacking`, `17-it-generator`, `04-text-byte` (bytes, encodings), `08-def-type-hints`,
`15-more-types` (Protocol, TypeVar, overload), `06-obj-ref` (aliasing, weakref).

**Fit: good, with the same inversion as §3.1.** No statements, but small, self-contained,
pytest-and-doctest-covered classes that already are the shape of a `solve()` — Vector with
`__add__`/`__radd__`, the `Quantity` descriptor, `Tombola` as an ABC. Nothing here needs a hosted
judge, a fixture or interactive I/O.

**Attribution.** MIT, same handling as above: `source: fluentpython/example-code-2e
23-descriptor (MIT, adapted)`. Note the book's *prose* is O'Reilly's and is not in the repo — only
adapt what is in the repository.

**Yield: 15–20 tasks**, and they land in `advanced`, which is 19 of 189 today. This is the highest
value-per-task source in the note even though it is not the largest.

**Fills:** §2.1 nearly in full, plus `bytes`/`codecs`/`memoryview` and `weakref` from §2.2.

### 3.3 The CPython documentation's code examples — **adopt as a well, not as a source**

<https://github.com/python/cpython> · **Zero-Clause BSD** for code in the documentation — verified
from `LICENSE`, §"ZERO-CLAUSE BSD LICENSE FOR CODE IN THE PYTHON DOCUMENTATION" (line 265):
"Permission to use, copy, modify, and/or distribute this software for any purpose with or without
fee is hereby granted."

0BSD is the most permissive licence in this note — it requires **no attribution at all**. The
surrounding prose is the PSF licence, which is permissive but is not 0BSD, so the rule is: adapt
the *examples*, write the words fresh.

**Fit: it is not an exercise collection**, and pretending otherwise would be padding. What it is:
the `itertools` recipes, the `sqlite3` and `struct` and `decimal` and `ipaddress` and `zoneinfo`
tutorials, the logging cookbook, the `functools` and `contextlib` HOWTOs — every one of them a
worked, deterministic, 10-line example of a module drillion has never touched.

**Yield: 20–30 tasks**, but each one costs a full authoring session because the whole statement is
drillion's. Treat it as the reference to reach for when §2.2 says a module is missing, not as a
batch to work through.

**Fills:** most of §2.2, and it is the only well-licensed source that does.

### 3.4 MBPP (Mostly Basic Python Problems) — **adopt selectively**

<https://github.com/google-research/google-research/tree/master/mbpp> · **CC-BY-4.0** — verified
from the dataset card at <https://huggingface.co/datasets/google-research-datasets/mbpp>
(`license: cc-by-4.0`). Note the enclosing `google-research` repository is Apache-2.0; the dataset
carries its own, more specific licence, which is the one `NOTICE` already records.

974 crowd-sourced problems (427 hand-verified in `sanitized-mbpp.json`), each a one-line
`prompt`, a `code` solution and three `assert` test cases.

**Fit: mechanically perfect, editorially thin.** `{prompt, code, test_list}` maps one-to-one onto
`{## Rules, _reference, known cases in test_solve}`, and `187_job_spacing` already proves the
pipeline. But the median MBPP problem is "write a function to find the shared elements of two
lists" — a `sets` task, and drillion has eight. The signal is in the tail.

**Attribution.** CC-BY-4.0 permits adaptation and commercial redistribution and requires
attribution plus an indication of changes. `187_job_spacing`'s
`source: MBPP 39 (CC-BY-4.0, adapted)` plus the closing line satisfies it, and `NOTICE` already
carries the paragraph.

**Yield: 30–50** after filtering out everything the catalogue covers twice. Realistically the
useful slice is the regex, math, bit-twiddling and tuple-shaped problems.

**Fills:** parts of §2.3, some of `math`/`statistics` from §2.2. Nothing in §2.1.

### 3.5 gregmalcolm/python_koans — **adopt in small doses**

<https://github.com/gregmalcolm/python_koans> · **MIT** · verified from `MIT-LICENSE`.

Forty-odd `about_*.py` files of fill-in-the-blank assertions about language semantics:
`about_attribute_access`, `about_method_bindings`, `about_monkey_patching`, `about_scope`,
`about_class_attributes`, `about_multiple_inheritance`, `about_decorating_with_classes`,
`about_deleting_objects`, `about_proxy_object_project`.

**Fit: partial.** The koan format — assert a blank into truth — is not drillion's `solve()`, so
nothing transfers mechanically. What transfers is the *question list*: these files are a curated
inventory of the semantics that surprise people, which is exactly the genre of `044_mutabledefault`
("predict the leak") and `053_copy` ("predict the damage"). drillion has two such tasks and they
are among its best.

**Attribution.** MIT, `source: gregmalcolm/python_koans about_method_bindings (MIT, adapted)`.

**Yield: 10–15 tasks**, all in the predict-the-behaviour genre.

**Fills:** the MRO, monkey-patching, `__getattr__` and scope corners of §2.1.

### 3.6 The near misses

| source | licence | verdict |
|---|---|---|
| [openai/human-eval](https://github.com/openai/human-eval) | MIT (verified, `LICENSE`) | **Marginal.** 164 problems, docstring + canonical solution + tests, ideal shape. But they are deliberately entry-level and overlap `core` almost completely. Maybe 10–15 non-duplicative tasks. Take it only after §3.1–§3.4 are exhausted. |
| [norvig/pytudes](https://github.com/norvig/pytudes) | MIT (verified) | **Marginal.** Superb `hard`-tier material (Cryptarithmetic, Boggle, Countdown, How To Count Things), but most notebooks run past 30 minutes and a large share are Advent of Code or Project Euler solutions whose *statements* are unusable (§4.1, §4.3). 5–8 tasks, each expensive. |
| [evalplus/evalplus](https://github.com/evalplus/evalplus) | Apache-2.0 (verified) | **Use as a tool, not a source.** MBPP+/HumanEval+ add ~35× more test cases to problems that already exist. Valuable for hardening a `_reference`; contributes no new problems. Apache-2.0 needs its own `NOTICE` paragraph if any of it ships. |
| [kyclark/tiny_python_projects](https://github.com/kyclark/tiny_python_projects) | MIT (verified) | **Poor fit.** Every project is an argparse CLI graded on stdout. drillion has exactly two argparse tasks on purpose; twenty-two would be a different platform. |
| [rougier/numpy-100](https://github.com/rougier/numpy-100) | MIT (verified) | **Poor fit.** numpy is nowhere in the catalogue, and the entries are one-line snippets with no problem to state. |
| [freeCodeCamp/freeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp) | BSD-3-Clause (verified) | **Poor fit.** The licence is fine; the Python curriculum is video-and-project shaped, with the graded work living outside the repo. |

## 4. Rejected on licence

These are not "worth a second look". Each fails the gate stated in AGENTS.md and in this repo's
`NOTICE` practice.

### 4.1 Project Euler — CC BY-NC-SA 4.0

<https://projecteuler.net/copyright> states the problems are licensed
Attribution-NonCommercial-ShareAlike 4.0 and that "problems must not be used for commercial
purposes". Two independent blockers for an MIT repo: **NC** contradicts MIT's grant to "use, copy,
modify, merge, publish, distribute, sublicense, and/or sell", and **SA** would force the derived
task text under CC BY-NC-SA. Reject. This also constrains §3.1 — see the warning there.

### 4.2 Rosetta Code — GFDL 1.2

Rosetta Code's own copyright page: content is contributed under the GNU Free Documentation License
version 1.2. GFDL is a documentation copyleft with invariant-section and transparent-copy
machinery, and the FSF itself notes it is incompatible with most software licences. Reject.

### 4.3 Advent of Code — no redistribution

The site's own about/FAQ: "Advent of Code is free to *use*, not free to copy", with explicit
guidance not to put puzzle text in repositories. Linking is permitted; restating is not. Reject.

### 4.4 CS50P — CC BY-NC-SA 4.0

Harvard's CS50 problem sets carry CC BY-NC-SA 4.0, and `cs50/problems` has no `LICENSE` file at
all. Same NC and SA blockers as §4.1. Reject.

### 4.5 dabeaz-course/practical-python and python-mastery — CC BY-SA 4.0

Both verified as CC-BY-SA-4.0 via the API. Excellent material, and `python-mastery` covers §2.1
almost as well as Fluent Python does. But share-alike on adapted task text means the README of any
derived task would have to be CC BY-SA while the repository around it is MIT — the exact
contamination the brief names. Reject unless a maintainer decides a per-file licence split is
acceptable, which it should not be.

### 4.6 The benchmark datasets with laundered statements — APPS, CodeContests, Project CodeNet

| repo | repo licence | why it is still a no |
|---|---|---|
| [hendrycks/apps](https://github.com/hendrycks/apps) | MIT (verified) | Statements scraped from Codeforces, AtCoder, Kattis and LeetCode. The MIT file covers the harness, not the problems. |
| [google-deepmind/code_contests](https://github.com/google-deepmind/code_contests) | Apache-2.0 (verified) | Same shape. Codeforces statements are themselves CC BY-SA 4.0, which is §4.5's problem again. |
| [IBM/Project_CodeNet](https://github.com/IBM/Project_CodeNet) | Apache-2.0 (verified) | Problem descriptions come from AIZU and AtCoder under their own separate terms. |

A permissive licence on a repository is not a permissive licence on content the repository
scraped. Reject all three.

### 4.7 No licence at all

`faif/python-patterns` (no `LICENSE`, confirmed 404 on the licence API and no such file in the
tree), `zhiwehu/Python-programming-exercises` (none), `pybites/challenges` (none),
`cs50/problems` (none). Unlicensed means all rights reserved. Reject.

### 4.8 Proprietary platforms

LeetCode, HackerRank, Codewars, CheckiO, Edabit, Real Python, Python Morsels, w3resource,
GeeksforGeeks. Terms of service forbid reuse; no licence exists to evaluate. Reject, and do not
"take inspiration" in a way that reproduces a statement.

## 5. Recommendation

**Adopt, in this order:**

1. **fluentpython/example-code-2e (MIT) — 15–20 tasks.** First, despite being the smallest, because
   it fills the gap nothing else touches (§2.1) and it lands in `advanced`, the tier with 19 of 189
   tasks. Descriptors, ABCs, `__slots__`, operator overloading and the iterator protocol as a class
   are the difference between a catalogue that teaches Python and one that teaches the first half
   of Python.
2. **TheAlgorithms/Python (MIT) — 40–60 tasks.** Highest raw yield and the lowest cost per task,
   because the correct implementation and its doctests already exist and drop into `_reference`.
   Excluding `project_euler/` and the numpy-dependent directories.
3. **CPython docs, 0BSD examples — 20–30 tasks, drawn on demand.** Not a batch. The standing answer
   to "§2.2 says we have no `struct` task"; 0BSD asks for nothing in return.

**Then, if more is wanted:** MBPP's tail (CC-BY-4.0, 30–50, precedent already in `NOTICE`) and
python_koans (MIT, 10–15) for predict-the-behaviour tasks.

**Reject and do not revisit:** Project Euler, Rosetta Code, Advent of Code, CS50P, both Beazley
courses, DS-1000, APPS, CodeContests, Project CodeNet, `python-patterns`, `zhiwehu`,
`pybites/challenges`, and every commercial platform. Every one of these fails on licence, not on
quality, and no amount of rewriting fixes a share-alike or a non-commercial clause.

## 6. Open questions for a maintainer

1. **Does `source:` cover a reference implementation, or only a problem statement?** Both top
   recommendations invert the usual adaptation: drillion takes the *code* and writes the *words*.
   Arguably a freshly-written statement over an independently-expressible algorithm needs no
   attribution at all — but the repo's habit is to record provenance, and habits are cheaper than
   case-by-case judgement. Recommend recording it either way; needs a ruling before the first task
   lands.
2. **Does drillion want algorithms?** §3.1 is CS-course flavoured, and AGENTS.md's "categorical
   pragmatism" says people are here to get better at Python, not to prepare for a whiteboard. Graph
   traversal and DP are defensible as Python practice; a segment tree probably is not. Someone has
   to draw that line, and it decides whether §3.1's yield is 60 or 25.
3. **Should `advanced` grow?** 19 of 189 today. §3.2 would roughly double it. That is a deliberate
   shift in what the catalogue is, not a content top-up.
4. **Is Apache-2.0 acceptable in `NOTICE`?** Only EvalPlus needs it, and only if its tests ship.
   Apache-2.0 carries a `NOTICE`-propagation requirement MIT and CC-BY do not. Easiest answer is to
   use EvalPlus as a local check and ship nothing from it.
5. **Numbering.** §3.1 alone is 40–60 append-only folders after 201. ADR-0006 forbids inserting, so
   the curriculum order and the folder order will diverge further. Worth confirming that is
   accepted before adding a block this size.
