---
title: string-methods — turn a DNA strand into its RNA partner
difficulty: medium
tier: core
minutes: 10
prereqs: [11, 18]
tags: [string-methods]
source: exercism/python practice/rna-transcription (MIT, adapted)
---
# string-methods — turn a DNA strand into its RNA partner

*rna-transcription — a one-to-one character swap, and why four .replace() calls fail.*

## Read first
- [str.translate()](https://devdocs.io/python~3.14/library/stdtypes#str.translate) — `str.maketrans` and `translate`: build the mapping once, apply it in one pass
- [str.join()](https://devdocs.io/python~3.14/library/stdtypes#str.join) — `"".join` over a generator, the readable way to build a string character by character
- [str.replace()](https://devdocs.io/python~3.14/library/stdtypes#str.replace) — read this one to see the trap: each `replace()` runs over the result of the previous one
- [Mapping types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — the four-entry lookup table, if you prefer a dict to `maketrans`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A bioengineering team designs a molecule that switches off one misbehaving protein. To build it they need the RNA strand that pairs with a given piece of DNA, which means swapping every letter for its partner. One wrong letter and the molecule binds to something else entirely. Underneath the biology it is the most common string job there is — a fixed, one-to-one character mapping — and it hides the classic bug where you translate a letter and then translate your own output by mistake.

## Introduction
You work for a bioengineering company that specializes in developing therapeutic solutions.

Your team has just been given a new project to develop a targeted therapy for a rare type of cancer.

> [!NOTE]
> It's all very complicated, but the basic idea is that sometimes people's bodies produce too much of a given protein.
> That can cause all sorts of havoc.
>
> But if you can create a very specific molecule (called a micro-RNA), it can prevent the protein from being produced.
>
> This technique is called [RNA Interference][rnai].

[rnai]: https://admin.acceleratingscience.com/ask-a-scientist/what-is-rnai/

## Instructions
Your task is to determine the RNA complement of a given DNA sequence.

Both DNA and RNA strands are a sequence of nucleotides.

The four nucleotides found in DNA are adenine (**A**), cytosine (**C**), guanine (**G**), and thymine (**T**).

The four nucleotides found in RNA are adenine (**A**), cytosine (**C**), guanine (**G**), and uracil (**U**).

Given a DNA strand, its transcribed RNA strand is formed by replacing each nucleotide with its complement:

- `G` -> `C`
- `C` -> `G`
- `T` -> `A`
- `A` -> `U`

> [!NOTE]
> If you want to look at how the inputs and outputs are structured, take a look at the examples in the test suite.

## You get
`dna_strand` — a string of the DNA letters A, C, G and T, e.g. `"ACGTGGTCTTAA"`. It may be empty.

> [!NOTE]
> Exercism's stub is `def to_rna(dna_strand)`. Here the function is `solve(dna_strand)`; nothing else about the task changes.

## You return
A string of the same length, holding the RNA complement.

## Rules
Replace each letter with its partner, leaving the order untouched:

| DNA | RNA |
| --- | --- |
| `G` | `C` |
| `C` | `G` |
| `T` | `A` |
| `A` | `U` |

An empty strand transcribes to an empty string. Note that A becomes U while T becomes A: two letters map onto A's neighbourhood, which is where careless solutions come apart.

```python
solve("C")             # -> "G"
solve("ACGTGGTCTTAA")  # -> "UGCACCAGAAUU"
solve("")              # -> ""
```

## Hints
### Hint 1
Every character turns into exactly one other character and nothing else moves — the output is always as long as the input. So this is a per-character lookup, not a series of search-and-replace passes over the whole string. (Try four chained `.replace()` calls on paper with 'AT' and watch the T become A and then that A become U.)
### Hint 2
Two routes, both fine. The readable one: a dict `{'G': 'C', 'C': 'G', ...}` and `"".join` of the looked-up value for each character. The idiomatic one: `str.maketrans(<the four DNA letters>, <their partners, in the same order>)` builds the table once and `str.translate` applies it in a single pass — worth knowing because interviewers notice it.
### Hint 3
Different data, same swap:

```python
table = str.maketrans('abc', 'xyz')
'cab'.translate(table)   # -> 'zxy'
```

Each character is looked at exactly once against the original table, so a letter you have just written can never be translated a second time — that is precisely what chained replaces get wrong.
