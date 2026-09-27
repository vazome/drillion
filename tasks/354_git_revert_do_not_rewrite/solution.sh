git revert --no-edit "$(git log --format=%H --grep='^enable {flag} by default$' -1)"
git push
