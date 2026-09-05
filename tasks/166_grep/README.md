---
title: files-text — search many files at once, with five flags that change the answer
difficulty: hard
tier: core
minutes: 25
prereqs: [38, 96, 115]
tags: [files-text]
source: exercism/python practice/grep (MIT, adapted)
---
# files-text — search many files at once, with five flags that change the answer

*grep — sort the flags into "which lines match" and "how they are printed", and the task falls apart into two easy halves.*

## Read first
- [`str.splitlines()`](https://docs.python.org/3/library/stdtypes.html#str.splitlines) — cutting a file's text into lines, and `keepends=True` if you would rather each line kept the newline it came with
- [`in` on strings](https://docs.python.org/3/reference/expressions.html#membership-test-operations) — the substring test this whole task is built on
- [`str.lower()`](https://docs.python.org/3/library/stdtypes.html#str.lower) — one way to make a comparison ignore case: change both sides, not one
- [`enumerate()`](https://docs.python.org/3/library/functions.html#enumerate) — line numbers with `start=1`, because files are numbered from one and Python is not
- [`str.split()`](https://docs.python.org/3/library/stdtypes.html#str.split) — turning `"-n -i -x"` into something you can ask membership questions about
- [`str.join()`](https://docs.python.org/3/library/stdtypes.html#str.join) — gluing the collected output back into the single string you return

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Searching text is the one tool nobody gets to opt out of: you will run some version of `grep` on the day a service starts failing, and the flags you reach for under pressure are exactly these five. Writing it once, by hand, is the fastest way to stop half-remembering them — in particular *why* `-l` silently cancels `-n`, and why the filename suddenly appears in front of every line the moment you search a second file. It is also a small, honest lesson in separating two decisions that beginners reliably tangle together: deciding which records survive a filter, and deciding how the survivors are formatted. Every report, every log query and every export you write later has that same seam in it.

## Introduction
You have taken a job at a local library helping organize their collection of old books.
The student patrons are often hunting for half-remembered quotes to cite in their term papers.
Rather than manually read every book from cover to cover, you decide to build a small tool to scan them, looking for these partial quotes.

## Instructions
Search files for lines matching a search string and return all matching lines.

The Unix [`grep`][grep] command searches files for lines that match a regular expression.
Your task is to implement a simplified `grep` command, which supports searching for fixed strings.

The `grep` command takes three arguments:

1. The string to search for.
2. Zero or more flags for customizing the command's behavior.
3. One or more files to search in.

It then reads the contents of the specified files (in the order specified), finds the lines that contain the search string, and finally returns those lines in the order in which they were found.
When searching in multiple files, each matching line is prepended by the file name and a colon (':').

### Flags

The `grep` command supports the following flags:

- `-n` Prepend the line number and a colon (':') to each line in the output, placing the number after the filename (if present).
- `-l` Output only the names of the files that contain at least one matching line.
- `-i` Match using a case-insensitive comparison.
- `-v` Invert the program -- collect all lines that fail to match.
- `-x` Search only for lines where the search string matches the entire line.

[grep]: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/grep.html

## You get
`solve(pattern, flags, files)` — three arguments.

`pattern` — the fixed string to look for, e.g. `"Agamemnon"`. It is never a regular expression and never empty.

`flags` — one string holding zero or more flags separated by single spaces, e.g. `"-n -i -x"`, or `""` when there are none. They may arrive in any order and any combination.

`files` — a `dict` mapping a file name to that whole file's text:

```python
{
    "iliad.txt": "Achilles sing, O Goddess! Peleus' son;\nHis wrath pernicious, who ten thousand woes\n",
    "midsummer-night.txt": "I do entreat your grace to pardon me.\n",
}
```

There is always at least one entry. Every file's text ends with a newline, and a file may be empty (`""`). The dict's order **is** the search order, the same way the order of file names on a real `grep` command line is.

> [!NOTE]
> Exercism's stub is `def grep(pattern, flags, files)` where `files` is a list of file *names* that the function opens and reads. Here the function is `solve(pattern, flags, files)` and `files` is a dict of `{name: contents}` — the text arrives already in memory. Nothing else about the task changes; see the first rule below.

## You return
One string: the whole output, with every line already ending in a newline, ready to be printed as-is. When nothing matches, that string is `""`.

## Rules
- **This task never touches the filesystem.** Exercism's instructions above talk about reading files, and every rule about *what* to search and *what* to print still applies exactly — but you are handed the contents instead of a path, so there is no `open()`, no `with`, and no encoding to worry about
- search the files in the order they appear in `files`, and each file's lines from the top; a file's lines are its text split on newlines, numbered from `1`
- a line matches when `pattern` appears anywhere in it. The flags change that test:
  - `-i` compares the line and the pattern with case ignored
  - `-x` requires the whole line to equal the pattern, rather than merely contain it
  - `-v` flips the answer — every line that would *not* have matched now does, and vice versa. It is applied last, after `-i` and `-x`
- what gets printed for a matching line, in this order: the file name and a colon **only when `files` holds more than one file**, then the line number and a colon **only when `-n` is set**, then the line itself, unchanged, including its trailing newline
- `-l` overrides all of that: print only the names of files that had at least one matching line, one per line, in `files` order, each name once, and ignore `-n` and the filename prefix entirely
- the file-name prefix depends on how many files were *handed to you*, not on how many of them matched: one file in, no prefixes, even under `-n`
- flags never conflict and are never repeated; an unknown flag is never passed in

```python
files = {"paradise-lost.txt": "Of Mans First Disobedience, and the Fruit\n"
                              "Of that Forbidden Tree, whose mortal tast\n"
                              "Brought Death into the World, and all our woe\n"}
solve("Forbidden", "", files)      # -> "Of that Forbidden Tree, whose mortal tast\n"
solve("Forbidden", "-n", files)    # -> "2:Of that Forbidden Tree, whose mortal tast\n"
solve("FORBIDDEN", "-i", files)    # -> "Of that Forbidden Tree, whose mortal tast\n"
solve("Forbidden", "-l", files)    # -> "paradise-lost.txt\n"
solve("Forbidden", "-x", files)    # -> ""
solve("Gandalf", "-n -l -x -i", files)   # -> ""
```

> [!WARNING]
> `-l` and `-n` together is a favourite trap: the answer is just the file names. `-l` decides the shape of the whole output, so once it is set the line numbers and the file-name prefix have nothing left to attach themselves to.

> [!WARNING]
> `-v` inverts the *match*, not the output. Under `-x -v` you keep every line that is not equal to the pattern — which is nearly all of them — rather than every line that does not contain it.

## Hints
### Hint 1
Five flags, but they are not five of the same kind of thing. Three of them change **which lines match**; two of them change **how the matches are printed**. Sort them into those two piles before you write anything, and the task stops being one hard problem and becomes two easy ones with a list of matches in between. While you are at it, note that one flag in the printing pile does not merely add to the output — it replaces it.

### Hint 2
Do one pass over the files and collect a small record for each match — which file, which line number, and the line itself — even for the runs where you will not end up printing two of those three. Inside the test, `-i` means normalising *both* the line and the pattern the same way, `-x` means swapping the "contains" question for an "equals" question, and `-v` means flipping whatever answer you arrived at rather than asking a different question. Then format: check the replacing flag first and return early if it is set, otherwise build each output line by putting on the pieces the flags call for, front to back. Two details that are easy to lose: line numbers start at `1`, and whether the file name goes on the front is decided by how many files you were given, not by how many produced a match.

### Hint 3
Different data, same shape — the invert flag, on a guest list:

```python
names = ["Ada", "Grace", "Alan", "Katherine"]
invert = False
[name for name in names if ("e" in name.lower()) != invert]   # -> ["Grace", "Katherine"]

invert = True
[name for name in names if ("e" in name.lower()) != invert]   # -> ["Ada", "Alan"]
```

`!=` between two booleans is "these two disagree", which is exactly what inverting means — so `-v` costs one comparison rather than a second copy of the matching code under an `if`. The other half of the lesson is the part this snippet does *not* do: it never decides how the surviving names should be printed. Keep those two decisions in different places and adding the fifth flag is a two-line change; tangle them and every new flag multiplies the branches.
