---
title: csv — parse quoted fields correctly
minutes: 10
prereqs: []
tags: [files-text]
---
# csv — parse quoted fields correctly

*split(',') corrupts real CSV the day a field grows a comma.*

## Why
Finance exports a spreadsheet of services and their owners as CSV
text. Some owner names are written "Last, First" and wrapped in quotes
because they contain a comma. A colleague's script that cuts each line
at every comma silently garbles those rows and puts the wrong owner on
the wrong service. You are asked to parse the export correctly so the
cost report is right.

## You get
`text` — one string of CSV text, first line the header, like
the example in the rules below. The test creates it and hands it to you;
you never build it yourself.

## You return
a list of dicts, one per data row, with the keys taken from
the header and every value kept as a string.

## Rules
Parse CSV text into a list of dicts, one per data row.

```
'service,owner,cpu\nauth,"Reyes, Ana",250m\ncron,priya,100m'
->
[{"service": "auth", "owner": "Reyes, Ana", "cpu": "250m"},
 {"service": "cron", "owner": "priya", "cpu": "100m"}]
```

The first line is the header. All values stay strings. Some owner
fields are quoted and contain a comma — split(",") shreds those rows,
which is the whole point of this drill.

text is a string, not a file: use io.StringIO to give the csv module
the file-like object it wants. No real files.

## Hints
### Hint 1
Count the commas on a quoted row: split(',') sees four fields where there are three. CSV quoting rules (commas inside quotes don't split, doubled quotes escape) are exactly what the csv module exists to handle — never reimplement them.
### Hint 2
csv.DictReader reads the header row itself and yields one dict per data row. It wants a file-like object, and io.StringIO(text) turns your string into one. Wrap the reader in list().
### Hint 3
Different data, same shape:

```python
import csv, io
raw = 'city,motto\nParis,"Fluctuat, nec mergitur"\nOslo,Blue'
print(list(csv.DictReader(io.StringIO(raw))))
# [{'city': 'Paris', 'motto': 'Fluctuat, nec mergitur'},
#  {'city': 'Oslo', 'motto': 'Blue'}]
print(raw.splitlines()[1].split(','))
# ['Paris', '"Fluctuat', ' nec mergitur"']   <- shredded
```

The reader undid the quotes; the naive split tore the field in half.
