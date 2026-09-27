git bisect start HEAD "$(git rev-list --max-parents=0 HEAD)"
git bisect run sh check.sh
git tag first-bad refs/bisect/bad
git bisect reset
