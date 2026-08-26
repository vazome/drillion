---
title: slicing — decode an RNA strand until the stop signal
difficulty: medium
tier: core
minutes: 15
prereqs: [88, 92, 95, 96, 97, 101]
tags: [slicing, dicts]
source: exercism/python practice/protein-translation (MIT, adapted)
---
# slicing — decode an RNA strand until the stop signal

*protein-translation — cut a string into fixed-size chunks, look each one up, and stop at the terminator.*

## Why
Every binary protocol you will ever debug works like this: a stream arrives, you cut it into fixed-width fields, you look each field up in a table, and somewhere in the stream there is a value that means "stop reading now". Getting the chunking right and honouring the terminator is most of what a parser does. RNA is a friendly version of the problem — the chunks are three characters, the table has seventeen rows, and the terminator is three of them — so you can concentrate on the shape rather than on byte order.

## Instructions
Your job is to translate RNA sequences into proteins.

RNA strands are made up of three-nucleotide sequences called **codons**.
Each codon translates to an **amino acid**.
When joined together, those amino acids make a protein.

In the real world, there are 64 codons, which in turn correspond to 20 amino acids.
However, for this exercise, you’ll only use a few of the possible 64.
They are listed below:

| Codon              | Amino Acid    |
| ------------------ | ------------- |
| AUG                | Methionine    |
| UUU, UUC           | Phenylalanine |
| UUA, UUG           | Leucine       |
| UCU, UCC, UCA, UCG | Serine        |
| UAU, UAC           | Tyrosine      |
| UGU, UGC           | Cysteine      |
| UGG                | Tryptophan    |
| UAA, UAG, UGA      | STOP          |

For example, the RNA string “AUGUUUUCU” has three codons: “AUG”, “UUU” and “UCU”.
These map to Methionine, Phenylalanine, and Serine.

### “STOP” Codons

You’ll note from the table above that there are three **“STOP” codons**.
If you encounter any of these codons, ignore the rest of the sequence — the protein is complete.

For example, “AUGUUUUCUUAAAUG” contains a STOP codon (“UAA”).
Once we reach that point, we stop processing.
We therefore only consider the part before it (i.e. “AUGUUUUCU”), not any further codons after it (i.e. “AUG”).

Learn more about [protein translation on Wikipedia][protein-translation].

[protein-translation]: https://en.wikipedia.org/wiki/Translation_(biology)

## You get
`strand` — an RNA string, upper case, whose length is always a multiple of three:

```python
"AUGUUUUGG"
```

Every three-letter group in it is one of the seventeen codons in the table above; nothing else appears.

> [!NOTE]
> Exercism's stub is `def proteins(strand)`. Here the function is `solve(strand)`; nothing else about the task changes.

## You return
A `list` of amino acid names (`str`), in the order they appear in the strand.

```python
solve("AUGUUUUGG")  # -> ["Methionine", "Phenylalanine", "Tryptophan"]
solve("UAA")        # -> []
```

## Rules
- cut the strand into three-character codons, left to right
- translate each codon with the table above; the names are spelled exactly as printed, capital first letter and the rest lower case
- the moment you meet a STOP codon (`UAA`, `UAG` or `UGA`), stop — it is not in the result, and neither is anything after it
- a strand that begins with a STOP codon gives `[]`, and so does the empty strand

```python
solve("UGG")                 # -> ["Tryptophan"]
solve("AUGUUUUAA")           # -> ["Methionine", "Phenylalanine"]
solve("UGGUAGUGG")           # -> ["Tryptophan"]
solve("UGGUGUUAUUAAUGGUUU")  # -> ["Tryptophan", "Cysteine", "Tyrosine"]
```

> [!WARNING]
> `"AUGAUG"` is two Methionines, not a stop: `UGA` only counts when it sits on a codon boundary. If you search for `"UGA"` anywhere in the string instead of stepping three characters at a time, this case fails.

## Read first
- [Mapping types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) — a codon table is a dict; seventeen keys is nothing
- [Slicing](https://docs.python.org/3/reference/expressions.html#slicings) — `strand[i:i + 3]` combined with `range(0, len(strand), 3)` is the chunker
- [break](https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops) — leaving a loop early is the whole STOP rule
- [textwrap.wrap()](https://docs.python.org/3/library/textwrap.html#textwrap.wrap) — an alternative chunker, if you would rather not write the `range` yourself

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Two decisions, and neither depends on the other: how you cut the string into threes, and what you do when a chunk turns out to be a STOP. Write the table as a dict literal first — it is the boring part, get it out of the way — and notice that four codons share the name `Serine`, so several keys map to the same value.
### Hint 2
Step through the strand three characters at a time and collect names into a list. Reach for `break` rather than a flag variable: the STOP codon means "this loop is finished", which is exactly what `break` says. Keep the STOP codons in the same dict as everything else, mapped to the string `"STOP"`, so the lookup is one operation and the check afterwards is one comparison — a separate set of stop codons is a second thing that can drift out of step with the first.
### Hint 3
Different data, same "chunk, look up, stop at the sentinel" shape — reading a fixed-width device log until the shutdown marker:

```python
CODES = {'01': 'boot', '02': 'read', '03': 'write', 'FF': 'halt'}

def events(frame):
    out = []
    for start in range(0, len(frame), 2):
        name = CODES[frame[start:start + 2]]
        if name == 'halt':
            break
        out.append(name)
    return out

events('010203FF0102')  # -> ['boot', 'read', 'write']
```

The trailing `0102` is never reached, because `break` ends the loop rather than skipping one item.
