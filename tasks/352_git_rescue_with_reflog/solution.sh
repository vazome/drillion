git branch feature/{feature} "$(git log -g -1 --format=%H --grep-reflog='commit: add {feature} tests' HEAD)"
git reset --hard "$(git log -g -1 --format=%H --grep-reflog='commit: add {lost}' HEAD)"
