---
title: shutil / tempfile / glob — stage files, then clean up
minutes: 18
prereqs: []
tags: [stdlib-ops]
---
# shutil / tempfile / glob — stage files, then clean up

*Staging files in scratch space and tidying up afterwards is half of build tooling.*

## Why
A build job tidies a work folder: log files get copied to a scratch
area for upload, temporary files get moved out of the way. The scratch
area must be a fresh, uniquely named folder (two jobs on the same
machine must not collide) and it must be removed afterward even if
something fails halfway. The release engineer wants a report of what was
copied, moved, staged and left behind.

## You get
`root` — a string path to a folder holding files and no
subfolders, like "/tmp/ex040_abc". The test creates it and hands you the
path; you never build it yourself.

## You return
a dict with the keys "copied", "moved", "staged" and "left"
(each a sorted list of bare filenames) and "cleaned" (True if the
scratch folder is gone).

## Rules
`root` is a directory path as a STRING, holding a flat pile of files:
some *.log, some *.tmp, some with other extensions. No subdirectories.

Stage the interesting ones in scratch space and leave no mess behind:

  1. Make a scratch directory with tempfile — not a hardcoded /tmp/staging.
  2. COPY every *.log from root into it. The originals stay in root.
  3. MOVE every *.tmp from root into it. The originals leave root.
  4. Note what ended up in the scratch directory, then delete it.

Return, with basenames only and never full paths:

```
{"copied":  ["api.log", "web.log"],              # what you copied, sorted
 "moved":   ["build.tmp"],                       # what you moved, sorted
 "staged":  ["api.log", "build.tmp", "web.log"], # in scratch before you deleted it, sorted
 "left":    ["api.log", "notes.txt", "web.log"], # still in root at the end, sorted
 "cleaned": True}                                # the scratch directory is gone
```

Match files with glob and a pattern, not by filtering os.listdir yourself.
Copy with a shutil function that keeps the timestamps. os.path.basename
turns a path into a bare filename.

tempfile.TemporaryDirectory() used as a `with` block does step 1 and the
delete in step 4 for you, including when something raises halfway through —
which is the reason it exists.

## Hints
### Hint 1
Three modules, one job each. tempfile invents a scratch path nobody else is using, so two runs of your script on the same box cannot collide. glob expands a shell-style pattern into real paths. shutil is the file operations you would otherwise shell out to cp, mv and rm -r. The one thing to be careful about: glob hands you full paths, and the answer wants bare filenames.
### Hint 2
glob.glob(os.path.join(root, '*.log')) lists the matches. shutil.copy2 copies a file into a directory and keeps its metadata; shutil.move moves one. os.listdir gives you the names already bare. Wrap the whole thing in `with tempfile.TemporaryDirectory() as stage:` and take your staged listing before the block ends — outside it the directory is gone, which is exactly how you check 'cleaned' with os.path.exists.
### Hint 3
Different tree, same moves:

```python
import glob, os, shutil, tempfile
with tempfile.TemporaryDirectory() as stage:
    for path in glob.glob('/var/backups/*.sql'):
        shutil.copy2(path, stage)
        print(os.path.basename(path))    # dump-2024.sql
    print(sorted(os.listdir(stage)))     # ['dump-2024.sql']
print(os.path.exists(stage))             # False — the with block removed it
```

Scratch space you did not name, and cleanup you cannot forget.
