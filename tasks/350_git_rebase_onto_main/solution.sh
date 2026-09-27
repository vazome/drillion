git switch feature/{feature}
git rebase main || true
printf '%s\n' 'PAGE_SIZE = {size}' > limits.py
git add limits.py
GIT_EDITOR=true git rebase --continue
git switch main
git merge --ff-only feature/{feature}
git branch -d feature/{feature}
