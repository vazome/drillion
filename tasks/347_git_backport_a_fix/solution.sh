git switch release/1.{minor}
git cherry-pick "$(git log main --format=%H --grep='^fix {bug}$')"
git switch main
