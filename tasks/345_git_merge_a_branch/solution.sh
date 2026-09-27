git merge --ff-only feature/{a}
git merge --no-ff --no-edit feature/{b}
git branch -d feature/{a} feature/{b}
